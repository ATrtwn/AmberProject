import pandas as pd

# Read the CSV files
demographics_df = pd.read_csv('demographic_info.csv')
diagnosis_df = pd.read_csv('Respiratory_Sound_Database/patient_diagnosis.csv', header=None, names=['Patient_ID', 'Disease'])

# Merge the dataframes on Patient_ID
merged_df = demographics_df.merge(diagnosis_df, on='Patient_ID', how='left')

# Display the first few rows to verify the merge
print("First 10 rows of merged dataframe:")
print(merged_df.head(10))

# Display info about the merge
print(f"\nOriginal demographics shape: {demographics_df.shape}")
print(f"Original diagnosis shape: {diagnosis_df.shape}")
print(f"Merged dataframe shape: {merged_df.shape}")

# Check for any missing diseases
missing_diseases = merged_df[merged_df['Disease'].isna()]
if len(missing_diseases) > 0:
    print(f"\nPatients with missing disease information: {len(missing_diseases)}")
    print(missing_diseases['Patient_ID'].tolist())

# Save the merged dataframe
merged_df.to_csv('demographic_info_with_disease.csv', index=False)
print(f"\nMerged dataframe saved as 'demographic_info_with_disease.csv'")

# Display unique diseases
print(f"\nUnique diseases in the dataset:")
print(merged_df['Disease'].value_counts()) 