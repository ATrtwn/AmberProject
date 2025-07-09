import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load your data
data = pd.read_csv('../data/df_combined_all.csv')

# Features and target
X = data.drop(columns=["Disease"]).drop(columns=data.columns[0])
y = data["Disease"]

# replacement of all the columns with object type (True/False as strings)
object_columns = X.select_dtypes(include=['object']).columns
for col in object_columns:
    # Strip any whitespace in the column, replace 'True' with 1 and 'False' with 0
    X[col] = X[col].str.strip().replace({'True': 1, 'False': 0})
    # Set any other non-1/0 value to NaN
    X[col] = pd.to_numeric(X[col], errors='coerce')

# Encode the target labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Test the model
y_pred = rf_model.predict(X_test)


# Save the trained model, label encoder, and column names
joblib.dump(rf_model, 'random_forest_model.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')
joblib.dump(X.columns.tolist(), 'column_names.pkl')
