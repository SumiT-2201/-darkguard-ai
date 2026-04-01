import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import Config

def create_app():
    # Frontend directory is two levels up from backend/app
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize DB (MongoDB)
    from app.services.mongo_service import MongoService
    app.db = MongoService(app.config['MONGO_URI'], app.config['MONGO_DB_NAME'])

    # Load ML Model
    try:
        from app.services.ml_detector import MLDetector
        MLDetector.load_model()
    except Exception as e:
        print(f"⚠️ ML Model failed to load (run training first!): {e}")

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
        
    @app.route('/api/health')
    def health():
        return jsonify({"status": "healthy", "service": "DarkGuard API"})

    return app
