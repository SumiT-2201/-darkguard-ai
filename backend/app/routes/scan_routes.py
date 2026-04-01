from flask import Blueprint, request, jsonify, current_app
from app.services.scraper import Scraper
from app.services.hybrid_detector import HybridDetector
from app.services.score_engine import ScoreEngine
from app.services.report_generator import ReportGenerator

scan_bp = Blueprint('scan_bp', __name__)

@scan_bp.route('/scan', methods=['POST', 'OPTIONS'])
def run_scan():
    # CORS Preflight handler - already handled by before_request but added for route robustness
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    url = data['url']
    print(f"📡 Incoming scan request for URL: {url}")
    
    try:
        scraper = Scraper(url)
    except ValueError as ve:
        print(f"❌ URL Validation Error: {ve}")
        return jsonify({"status": "error", "message": str(ve)}), 400
    
    try:
        html_content, text_content, page_meta, status_info = scraper.fetch()
        
        if not html_content:
            print(f"❌ Scraper failed for {url}: {status_info.get('message')}")
            return jsonify(status_info), 400

        all_detections = HybridDetector.analyze_and_merge(html_content, text_content)

        score_data = ScoreEngine.calculate_trust_score(all_detections)
        report = ReportGenerator.build_report(url, page_meta, score_data, all_detections)
        
        # Merge status info into response
        response_data = {
            "status": status_info["status"],
            "message": status_info.get("message"),
            "fallback_used": status_info.get("fallback_used"),
            "report": report
        }
        
        if hasattr(current_app, 'db') and current_app.db is not None:
            current_app.db.save_scan(report)
        
        print(f"✅ Scan completed successfully for {url}")
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"🔥 Critical Backend Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Server processing error: {str(e)}"}), 500

@scan_bp.route('/test', methods=['GET', 'OPTIONS'])
def test_backend():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
    return jsonify({
        "status": "success",
        "message": "Backend is running"
    })
