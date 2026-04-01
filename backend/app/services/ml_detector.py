import os
import joblib
import nltk
from app.config import Config
from app.ml.feature_extraction import clean_text

class MLDetector:
    model = None
    vectorizer = None
    label_encoder = None
    
    # 1. Exclusion List for common benign sentences detected by ML erroneously
    EXCLUSION_LIST = [
        "login", "sign up", "forgot password", "new chat", "search for anything",
        "menu bar", "home page", "back to previous", "create an account",
        "accept and continue", "view profile", "privacy policy", "terms of use",
        "help center", "contact us", "all rights reserved"
    ]

    @classmethod
    def load_model(cls):
        try:
            # Ensure tokenize resources are available
            nltk.download('punkt', quiet=True)
            cls.model = joblib.load(Config.ML_MODEL_PATH)
            cls.vectorizer = joblib.load(Config.ML_VECTORIZER_PATH)
            le_path = os.path.join(os.path.dirname(Config.ML_MODEL_PATH), 'label_encoder.joblib')
            if os.path.exists(le_path):
                cls.label_encoder = joblib.load(le_path)
            print("✅ ML Model Loaded Successfully")
        except FileNotFoundError:
            print("⚠️ ML Model not found. Did you run the training script? ML detection won't work.")
            cls.model = None
            cls.vectorizer = None
        except Exception as e:
            print(f"⚠️ Error loading ML model: {e}")

    @classmethod
    def predict(cls, text_content):
        if cls.model is None or cls.vectorizer is None:
            return []
        try:
            sentences = nltk.tokenize.sent_tokenize(text_content)
        except LookupError:
            sentences = text_content.split(' | ')

        detections = []
        # Filter for sentences that look like they could contain patterns
        valid_sentences = [s for s in sentences if 10 < len(s) < 300]
        if not valid_sentences:
            return detections
            
        # Clean text exactly as it was during training
        cleaned_sentences = [clean_text(s) for s in valid_sentences]
            
        X_vec = cls.vectorizer.transform(cleaned_sentences)
        probs = cls.model.predict_proba(X_vec)
        preds = cls.model.predict(X_vec)
        
        for i, (prob, pred, sentence) in enumerate(zip(probs, preds, valid_sentences)):
            max_prob = max(prob)
            category = pred
            if cls.label_encoder is not None:
                category = cls.label_encoder.inverse_transform([pred])[0]
            
            # FALSE POSITIVE FILTER: Skip harmless UI phrases
            sent_lower = sentence.lower().strip()
            if any(exc in sent_lower for exc in cls.EXCLUSION_LIST):
                continue
            
            # USE IMPROVED THRESHOLD (0.8 as requested)
            if category.lower() in ['not_dark_pattern', 'none', 'safe'] or max_prob < 0.8:
                continue
            
            # Limit duplicates for each category
            if len([d for d in detections if d['category'] == category]) > 5:
                continue

            detections.append({
                "pattern_name": f"ML Detection ({category.replace('_', ' ').replace('-', ' ').title()})",
                "category": category.lower(),
                "matched_text": sentence,
                "severity": "high" if max_prob > 0.95 else "medium",
                "detection_method": "ml-based",
                "confidence": round(float(max_prob), 2)
            })
            
        return detections
