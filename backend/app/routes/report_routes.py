from flask import Blueprint, jsonify, current_app
from bson.objectid import ObjectId

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/history', methods=['GET'])
def get_history():
    if not hasattr(current_app, 'db') or current_app.db is None:
        return jsonify({"status": "error", "message": "Database not configured"})
        
    try:
        history = current_app.db.get_history(limit=50)
        return jsonify({"success": True, "data": history})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@report_bp.route('/report/<report_id>', methods=['GET'])
def get_report(report_id):
    if not hasattr(current_app, 'db') or current_app.db is None:
        return jsonify({"status": "error", "message": "Backend database not configured"})
        
    try:
        report = current_app.db.get_report(report_id)
        if not report:
            return jsonify({"status": "error", "message": "Report not found"}), 404
            
        return jsonify({"status": "success", "report": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
