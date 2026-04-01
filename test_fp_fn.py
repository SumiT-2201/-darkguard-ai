import os
import joblib
import pandas as pd
import sys
import nltk
import re
import string

# Setup environment to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.config import Config

# Local text cleaning specifically for evaluation parity
def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    STOP_WORDS = {"i", "me", "my", "we", "our", "you", "your", "he", "him", "she", "her", "it", "they", "them"}
    words = text.split()
    return " ".join([w for w in words if w not in STOP_WORDS])

def run_evaluation():
    dataset_path = 'dark_patterns_dataset.csv'
    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}")
        return

    df = pd.DataFrame(pd.read_csv(dataset_path))
    
    # Load model and vectorizer
    model_path = Config.ML_MODEL_PATH
    vectorizer_path = Config.ML_VECTORIZER_PATH
    le_path = os.path.join(os.path.dirname(model_path), 'label_encoder.joblib')

    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        print("Model or vectorizer not found. Please train the model first.")
        return

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    label_encoder = None
    if os.path.exists(le_path):
        label_encoder = joblib.load(le_path)

    # Clean text
    df['clean_text'] = df['text'].apply(clean_text)
    X_vec = vectorizer.transform(df['clean_text'])
    
    probs = model.predict_proba(X_vec)
    preds = model.predict(X_vec)

    results = []
    tp, tn, fp, fn = 0, 0, 0, 0
    fp_cases = []
    fn_cases = []

    for i, row in df.iterrows():
        actual = row['label'].lower()
        pred_idx = preds[i]
        prob = max(probs[i])
        
        # Determine category name
        if label_encoder:
            pred_label = label_encoder.inverse_transform([pred_idx])[0].lower()
        else:
            pred_label = str(pred_idx).lower()

        # --- REPLACED HARDCODED 0.7 WITH GLOBAL CONFIG ---
        is_dark_pattern_actual = actual != 'safe'
        is_dark_pattern_pred = (pred_label != 'safe') and (prob >= Config.CONFIDENCE_THRESHOLD)

        if is_dark_pattern_actual and is_dark_pattern_pred:
            tp += 1
        elif not is_dark_pattern_actual and not is_dark_pattern_pred:
            tn += 1
        elif not is_dark_pattern_actual and is_dark_pattern_pred:
            fp += 1
            fp_cases.append((row['text'], pred_label, prob))
        elif is_dark_pattern_actual and not is_dark_pattern_pred:
            fn += 1
            fn_cases.append((row['text'], actual, prob, pred_label))

    results_summary = {
        "Total Samples": len(df),
        "True Positives (TP)": tp,
        "True Negatives (TN)": tn,
        "False Positives (FP)": fp,
        "False Negatives (FN)": fn,
        "Precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0,
        "Recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
        "Threshold_Used": Config.CONFIDENCE_THRESHOLD,
        "FP_Cases": [{"text": t, "pred": p, "conf": round(c, 2)} for t, p, c in fp_cases[:5]],
        "FN_Cases": [{"text": t, "actual": a, "conf": round(c, 2), "pred": p} for t, a, c, p in fn_cases[:5]]
    }
    
    import json
    with open('eval_metrics.json', 'w') as f:
        json.dump(results_summary, f, indent=4)
    print(f"Done. Metrics saved to eval_metrics.json using threshold {Config.CONFIDENCE_THRESHOLD}")

if __name__ == '__main__':
    run_evaluation()
