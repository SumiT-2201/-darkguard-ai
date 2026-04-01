import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_root, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)

# Automatic API Key Generation for first-time startup
_api_key = os.environ.get('DARKGUARD_API_KEY')
if not _api_key:
    _api_key = secrets.token_hex(16)
    with open(env_path, 'a') as f:
        f.write(f"\nDARKGUARD_API_KEY={_api_key}\n")
    os.environ['DARKGUARD_API_KEY'] = _api_key

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'darkguard-ml-super-secret-key'
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'

    # Security: Root API Key for authentication
    API_KEY = _api_key

    # ML Detection Sensitivity
    CONFIDENCE_THRESHOLD = 0.75

    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'darkguard_db'

    # Update ML path to reflect the new location
    ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'trained_model', 'best_classifier.joblib')
    ML_VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'trained_model', 'tfidf_vectorizer.joblib')

    # LLM Configuration
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') or 'your-api-key-here'
    LLM_MODEL = "claude-3-5-sonnet-20241022" 
    LLM_CONFIDENCE_THRESHOLD = float(os.environ.get('LLM_CONFIDENCE_THRESHOLD') or 0.8)
