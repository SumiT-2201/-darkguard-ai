import os
import sys
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import Config

def create_app():
    # 1. Resolve Root Frontend path for static serving
    # Structure: backend/app/__init__.py -> backend -> root -> frontend
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    frontend_dir = os.path.join(root_dir, 'frontend')
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS for cross-origin requests (Extension)
    CORS(app)

    # Initialize DB (MongoDB)
    from app.services.mongo_service import MongoService
    app.db = MongoService(app.config['MONGO_URI'], app.config['MONGO_DB_NAME'])

    # Load ML Model for inference
    try:
        from app.services.ml_detector import MLDetector
        MLDetector.load_model()
    except Exception as e:
        print(f"⚠️ ML Model failed to load (run training first!): {e}")

    # --- 🔒 SECURITY MIDDLEWARE (API KEY AUTH) ---
    @app.before_request
    def authenticate():
        # Bypass authentication for:
        # 1. Static frontend files and root dashboard
        # 2. Health check route
        if request.path.startswith('/api/'):
            if request.path == '/api/health':
                 return None
            
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != app.config['API_KEY']:
                return jsonify({
                    "status": "error", 
                    "error": "Unauthorized", 
                    "message": "Missing or invalid X-API-Key"
                }), 401
        return None

    # Register API blueprints
    from app.routes.scan_routes import scan_bp
    from app.routes.report_routes import report_bp
    
    app.register_blueprint(scan_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)
        
    return app
