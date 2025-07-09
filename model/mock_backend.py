import numpy as np
import pandas as pd

# Define possible diagnoses
DIAGNOSES = ["Pneumonia", "Flu", "COVID-19", "Asthma"]

# Define all possible tests/features and their simulated importance weights
ALL_TESTS = {
    "fever": 0.6,
    "cough": 0.4,
    "chest X-ray": 1.2,
    "blood Test - CRP": 0.8,
    "o2 Saturation": 1.0,
    "ct Scan": 1.5,
    "fatigue": 0.3,
    "wheezing": 0.5,
    "loss of Smell": 1.1
}

# Fake logistic model coefficients (just made up for demonstration)
# Rows: Diagnoses, Cols: Features (order matters)
FAKE_COEFFICIENTS = {
    "Pneumonia": [0.3, 0.2, 1.5, 0.8, 1.1, 0.5, 0.1, 0.0, 0.0],
    "Flu": [1.0, 0.9, 0.2, 0.5, 0.4, 0.1, 0.8, 0.0, 0.0],
    "COVID-19": [2.0, 1.5, 0.9, 1.2, 1.5, 1.2, 0.4, 0.2, 2.5],
    "Asthma": [0.1, 0.5, 0.0, 0.2, 0.6, 0.0, 0.3, 1.2, -0.5],
}

# Convert to DataFrame for matrix ops
COEFF_DF = pd.DataFrame(FAKE_COEFFICIENTS, index=list(ALL_TESTS.keys())).T


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def mock_predict_proba(selected_tests):
    """
    Simulate logistic regression output given selected test results.

    selected_tests: dict of {test_name: bool}
    """
    # Create feature vector
    feature_vector = np.array([
        1 if selected_tests.get(test, False) else 0
        for test in ALL_TESTS
    ])

    # Calculate raw logits (linear combo)
    logits = COEFF_DF.values @ feature_vector

    # Apply sigmoid to simulate probabilities
    probs = sigmoid(logits)

    return dict(zip(DIAGNOSES, probs))


def get_all_tests():
    """Return test list for frontend checkboxes"""
    return list(ALL_TESTS.keys())
