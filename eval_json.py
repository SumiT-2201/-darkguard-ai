import joblib
import json
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Local imports
sys_path = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.join(sys_path, 'backend', 'app', 'ml'))

from backend.app.ml.dataset import get_dataset
from backend.app.ml.feature_extraction import clean_text

def run_eval():
    df = get_dataset()
    df['clean_text'] = df['text'].apply(clean_text)
    X = df['clean_text']
    y = df['label']
    
    # Load vectorizer and best model
    vec_path = os.path.join('backend', 'app', 'ml', 'trained_model', 'tfidf_vectorizer.joblib')
    model_path = os.path.join('backend', 'app', 'ml', 'trained_model', 'best_classifier.joblib')
    
    vectorizer = joblib.load(vec_path)
    model = joblib.load(model_path)
    
    X_vec = vectorizer.transform(X)
    
    # Actually just split identically as train loop to get test set
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)
    
    y_pred = model.predict(X_test)
    
    results = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "Recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "F1-Score": f1_score(y_test, y_pred, average='weighted', zero_division=0)
    }
    
    with open('eval.json', 'w') as f:
        json.dump(results, f)

if __name__ == '__main__':
    run_eval()
