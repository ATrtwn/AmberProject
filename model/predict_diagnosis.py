import joblib
import numpy as np
import pandas as pd

# Load the pre-trained RandomForest model, label encoder, and column names
rf_model = joblib.load('model/random_forest_model.pkl')
label_encoder = joblib.load('model/label_encoder.pkl')
column_names = joblib.load('model/column_names.pkl')

# Function to predict diagnosis
def predict_diagnosis(selected_tests):
    """
    Predict the diagnosis using the pre-trained RandomForest model based on the selected tests.
    selected_tests: dictionary with test names (keys) and boolean values (True/False).
    """
    # Ensure the selected tests match the column names (feature order)
    feature_vector = np.array([
        1 if selected_tests.get(test, False) else 0
        for test in column_names  # Use the saved column names to ensure correct order
    ])

    # Convert the feature vector into a DataFrame to match the model's expected input format
    feature_df = pd.DataFrame([feature_vector], columns=column_names)

    # Get predicted probabilities for each class using the pre-trained RandomForest model
    probs = rf_model.predict_proba(feature_df)[0]  # This will give probabilities for all classes

    # Return the probabilities as a dictionary with class names as keys
    return dict(zip(label_encoder.classes_, probs))