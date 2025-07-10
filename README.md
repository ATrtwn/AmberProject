# Clinical Symptom-Based Differential Diagnosis Tool

## Overview

This project provides a web-based interface for clinicians to enter unstructured text describing a patient's principal complaint and associated symptoms. The system extracts relevant features from the input and displays a graph-based differential diagnosis generated using a trained Random Forest classifier.

## Features
 
- 🤖 **Automated symptom extraction** using NLP  
- 📊 **Graphical differential diagnosis** output  
- 🌲 **Machine learning backend** powered by a Random Forest model  
- 🖥️ **Responsive and user-friendly interface**

## Project Structure

```text
clinical-dx-tool/
├── app.py                   # Main Flask app entry point
├── model/
│   └── random_forest.pkl    # Trained model
├── static/
│   ├── style.css            # CSS styles
│   └── script.js            # JavaScript for frontend interactivity
├── templates/
│   └── index.html           # HTML template for the main page
├── data/
│   └── symptoms.csv         # Training/testing datasets
├── utils/
│   └── extract_symptoms.py  # Symptom extraction logic
└── README.md                # Project documentation (this file)
```

## Getting Started

> Coming soon: instructions for installation, setup, and usage.

## Results/Graphs

> Coming soon

## Authors

Developed by [Team].