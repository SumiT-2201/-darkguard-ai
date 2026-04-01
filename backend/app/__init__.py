import os
import sys
from flask import Flask, send_from_directory, jsonify, request, make_response
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import Config

def create_app():
    # 1. Resolve Root Frontend path for static serving
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    frontend_dir = os.path.join(root_dir, 'frontend')
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS globally for all origins and headers (fix for extension and dashboard)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize DB (MongoDB)
    from app.services.mongo_service import MongoService
    app.db = MongoService(app.config['MONGO_URI'], app.config['MONGO_DB_NAME'])

    # Load ML Model for inference
    try:
        from app.services.ml_detector import MLDetector
        MLDetector.load_model()
    except Exception as e:
        print(f"⚠️ ML Model failed to load: {e}")

    # --- 🔒 SECURITY MIDDLEWARE (DEVELOPMENT-FRIENDLY AUTH) ---
    @app.before_request
    def authenticate():
        # A. ALWAYS Bypass for OPTIONS requests (CORS Preflight)
        if request.method == "OPTIONS":
            return make_response("", 200)

        # B. Bypass for static frontend files, root, and health checks
        if not request.path.startswith('/api/'):
             return None
             
        if request.path == '/api/health':
             return None

        # C. Localhost / Development Bypass
        # Allow requests from localhost without keys for easy dev setup
        host = request.headers.get('Host', '')
        if 'localhost' in host or '127.0.0.1' in host:
             return None

        # D. Conditional API Key Validation
        api_key = request.headers.get('X-API-Key')
        
        # If API key is provided, validate it. 
        # If missing, allow but log (making it optional for local browser testing)
        if api_key:
            if api_key != app.config['API_KEY']:
                return jsonify({
                    "status": "error", 
                    "error": "Unauthorized", 
                    "message": "Invalid X-API-Key provided"
                }), 401
        
        # No key provided? Allow the request to proceed (Optionally required for high-risk production environments)
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
