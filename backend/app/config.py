import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'darkguard-ml-super-secret-key'
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'

    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'darkguard_db'

    # Update ML path to reflect the new location
    ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'trained_model', 'best_classifier.joblib')
    ML_VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'trained_model', 'tfidf_vectorizer.joblib')

    # LLM Configuration
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') or 'your-api-key-here'
    LLM_MODEL = "claude-3-5-sonnet-20241022" # Using standard 3.5 Sonnet as default, or latest available
    LLM_CONFIDENCE_THRESHOLD = float(os.environ.get('LLM_CONFIDENCE_THRESHOLD') or 0.8)
