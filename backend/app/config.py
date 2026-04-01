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
