
print("get libraries...")
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.util import cos_sim
import torch
import re
import spacy
from negspacy.negation import Negex
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from spacy.language import Language
from spacy.util import filter_spans

print("Loading model and NLP pipeline, this may take a while...")
model = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")
nlp = spacy.load("en_core_web_sm")
print("Model and NLP loaded successfully")

def clean_text(text):
    # Lowercase everything
    text = text.lower()

    # Normalize common character issues
    text = text.replace('\u201c', '"').replace('\u201d', '"')  # fancy quotes
    text = text.replace('\u2013', '-')  # en-dash
    text = text.replace('\u2014', '-')  # em-dash
    text = text.replace('\xa0', ' ')   # non-breaking space

    # Normalize slashes between words
    text = re.sub(r'(?<=\w)/(?=\w)', ' and ', text)

    # Remove weird characters that might break tokenization
    text = re.sub(r'[^a-z0-9\s.,;:/()-]', ' ', text)

    # Optional: collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

@spacy.Language.component("set_keywords_as_ents")
def set_keywords_as_ents(doc, keywords):
    spans = []
    # Create spans for each matched and unmatched keyword
    for kw in keywords:
        for match in re.finditer(r"\b" + re.escape(kw.lower()) + r"\b", doc.text.lower()):
            start_char = match.start()
            end_char = match.end()
            span = doc.char_span(start_char, end_char, label="MATCHED")
            if span:
                spans.append(span)

    # Filter out overlapping spans
    filtered_spans = filter_spans(spans)

    # Ensure no overlap with existing entities
    existing_spans = set()
    for ent in doc.ents:
        existing_spans.update(range(ent.start, ent.end))

    # Only include spans that do not overlap with existing entities
    final_spans = [span for span in filtered_spans if not any(i in existing_spans for i in range(span.start, span.end))]

    # Set the new entities
    doc.ents = list(doc.ents) + final_spans
    return doc

def normalize(text):
    return re.sub(r'\W+', ' ', text.lower()).strip()

def extract_keywords_from_text(text):
    """
    Input: raw clinical text (string)
    Output: list of matched keywords found (not negated)
    """
    # Define the known variables the model was trained on
    possible_symptomps = [
        "fever", "cough", "chest X-ray", "blood Test - CRP",
        "o2 Saturation", "ct Scan", "fatigue", "wheezing", "loss of Smell"
    ]

    # Only add the negex component if it's not already in the pipeline
    if "negex" not in nlp.pipe_names:
        nlp.add_pipe("negex", last=True)

    # Clean text and parse it
    cleaned = clean_text(text)
    doc = nlp(cleaned)

    # Get negated entities from spaCy (e.g., "no fever" -> 'fever' is negated)
    negated_spans = {normalize(ent.text) for ent in doc.ents if ent._.negex}

    # Build normalized candidate n-grams (1 to 5 grams)
    tokens = re.findall(r'\w+', cleaned)
    candidate_phrases = set()
    for n in range(1, 6):
        for i in range(len(tokens) - n + 1):
            phrase = " ".join(tokens[i:i+n])
            candidate_phrases.add(normalize(phrase))

    # Filter out negated ones
    candidate_phrases = {p for p in candidate_phrases if p not in negated_spans}

    # Encode both candidates and known symptoms
    candidate_list = list(candidate_phrases)
    candidate_embeddings = model.encode(list(candidate_phrases), convert_to_tensor=True)
    matched_embeddings = model.encode(possible_symptomps, convert_to_tensor=True)

    threshold = 0.5
    found = []

    for i, kw in enumerate(possible_symptomps):
        kw_norm = normalize(kw)
        if kw_norm in negated_spans:
            print(f"Negated and skipped: {kw}")
            continue

        sim_scores = cos_sim(matched_embeddings[i], candidate_embeddings)[0]
        max_score = float(torch.max(sim_scores))
        best_match_idx = int(torch.argmax(sim_scores))
        best_match_phrase = candidate_list[best_match_idx]

        print(f"\nKeyword: '{kw}'")
        print(f"  Best match in text: '{best_match_phrase}'")
        print(f"  Similarity score: {max_score:.3f}")

        if max_score >= threshold:
            found.append(kw)

    return found