from flask import Flask, jsonify, request, send_from_directory, render_template
from model.predict_diagnosis import predict_diagnosis #, get_all_tests
from utils.text_to_symptom import extract_keywords_from_text, model, nlp
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnosis', methods=['POST'])
def get_diagnosis():
    data = request.get_json()
    selected_tests = data.get("selected_tests", [])

    # Probabilities with current selected tests
    selected = {test: True for test in selected_tests}
    probs = predict_diagnosis(selected)

    # Baseline probs: no tests selected
    baseline_probs = predict_diagnosis({})

    # Sort diagnoses by descending probability to keep order consistent
    df = pd.DataFrame(list(probs.items()), columns=["Diagnosis", "Probability"])
    df = df.sort_values("Probability", ascending=False)

    # Ensure baseline is ordered by same diagnoses
    baseline_df = pd.DataFrame(list(baseline_probs.items()), columns=["Diagnosis", "Probability"])
    baseline_df = baseline_df.set_index("Diagnosis").reindex(df["Diagnosis"]).reset_index()

    # Randomly assigning threshold values for each diagnosis
    thresholds = []
    np.random.seed(42)
    for diagnosis in df["Diagnosis"]:
        # Assign a random threshold value for each diagnosis (between 0.5 and 1.0, for example)
        threshold_value = round(np.random.uniform(0.5, 1.0), 2)
        thresholds.append([{"value": threshold_value, "class": 'Class A', "name": f'Next Step for {diagnosis}'}])

    return jsonify({
        "diagnoses": df["Diagnosis"].tolist(),
        "probabilities": df["Probability"].tolist(),
        "ground_probabilities": baseline_df["Probability"].tolist(),
        "thresholds": thresholds
    })

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    data = request.get_json()
    text = data.get('text', '')
    print("Received data:", data)

    matched = extract_keywords_from_text(text)
    print("Matched symptoms:", matched)

    return jsonify({"keywords": matched})

if __name__ == '__main__':
    print("Starting server after model loaded...")
    app.run(debug=True, use_reloader=False)
