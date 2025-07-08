import pandas as pd
import os
import glob
from collections import defaultdict

def extract_patient_id_from_filename(filename):
    """Extract patient ID from filename like '101_1b1_Al_sc_Meditron.txt' -> '101'"""
    return filename.split('_')[0]

def process_text_file(filepath):
    """Process a single text file to extract crackles and wheezes information."""
    crackles_present = False
    wheezes_present = False
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        crackles = int(parts[2])
                        wheezes = int(parts[3])
                        
                        if crackles == 1:
                            crackles_present = True
                        if wheezes == 1:
                            wheezes_present = True
                            
                        # If both are found, we can break early
                        if crackles_present and wheezes_present:
                            break
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    
    return crackles_present, wheezes_present

def extract_crackles_wheezes_from_files():
    """Extract crackles and wheezes information from all text files."""
    txt_files = glob.glob('audio_and_txt_files/*.txt')
    
    # Dictionary to store results for each patient
    patient_results = defaultdict(lambda: {'crackles': False, 'wheezes': False})
    
    print(f"Processing {len(txt_files)} text files...")
    
    for filepath in txt_files:
        filename = os.path.basename(filepath)
        patient_id = extract_patient_id_from_filename(filename)
        
        crackles, wheezes = process_text_file(filepath)
        
        # Update patient results (if any file has crackles/wheezes, mark as present)
        if crackles:
            patient_results[patient_id]['crackles'] = True
        if wheezes:
            patient_results[patient_id]['wheezes'] = True
    
    return patient_results

def main():
    # Extract crackles and wheezes information
    patient_results = extract_crackles_wheezes_from_files()
    
    # Read the merged dataframe
    merged_df = pd.read_csv('demographic_info_with_disease.csv')
    
    # Add crackles and wheezes columns
    crackles_list = []
    wheezes_list = []
    
    for patient_id in merged_df['Patient_ID']:
        patient_id_str = str(patient_id)
        if patient_id_str in patient_results:
            crackles_list.append(1 if patient_results[patient_id_str]['crackles'] else 0)
            wheezes_list.append(1 if patient_results[patient_id_str]['wheezes'] else 0)
        else:
            crackles_list.append(0)
            wheezes_list.append(0)
    
    merged_df['Crackles'] = crackles_list
    merged_df['Wheezes'] = wheezes_list
    
    # Save the updated dataframe
    merged_df.to_csv('demographic_info_with_disease_and_sounds.csv', index=False)
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total patients: {len(merged_df)}")
    print(f"Patients with crackles: {merged_df['Crackles'].sum()}")
    print(f"Patients with wheezes: {merged_df['Wheezes'].sum()}")
    print(f"Patients with both: {((merged_df['Crackles'] == 1) & (merged_df['Wheezes'] == 1)).sum()}")
    
    # Show some examples
    print(f"\nFirst 10 rows with sound information:")
    print(merged_df[['Patient_ID', 'Disease', 'Crackles', 'Wheezes']].head(10))
    
    print(f"\nPatients with crackles:")
    crackles_patients = merged_df[merged_df['Crackles'] == 1]
    print(crackles_patients[['Patient_ID', 'Disease', 'Crackles', 'Wheezes']].head(10))
    
    print(f"\nPatients with wheezes:")
    wheezes_patients = merged_df[merged_df['Wheezes'] == 1]
    print(wheezes_patients[['Patient_ID', 'Disease', 'Crackles', 'Wheezes']].head(10))

if __name__ == "__main__":
    main() 