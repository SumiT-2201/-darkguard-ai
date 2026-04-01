import json
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.report_generator import ReportGenerator

def test():
    url = "https://example-shop.com/product/123"
    meta = {"title": "Flash Sale - Exclusive Item", "description": "Buy now before it's gone!"}
    
    score_data = {
        "trust_score": 62,
        "grade": "D",
        "severity_counts": {"critical": 1, "high": 2, "medium": 1, "low": 0}
    }
    
    patterns = [
        {
            "category": "fake_urgency",
            "matched_text": "Only 2 items left!",
            "severity": "high",
            "detection_method": "ml-based",
            "confidence": 0.88
        },
        {
            "category": "hidden_costs",
            "matched_text": "Additional fees apply at checkout",
            "severity": "critical",
            "detection_method": "rule-based",
            "confidence": 1.0
        },
        {
            "category": "forced_action",
            "matched_text": "Sign up for newsletter to checkout",
            "severity": "high",
            "detection_method": "ml-based",
            "confidence": 0.76
        }
    ]
    
    report = ReportGenerator.build_report(url, meta, score_data, patterns)
    
    # Verify exact required fields
    required_fields = ["trust_score", "findings_list", "categories", "recommendations"]
    all_present = all(field in report for field in required_fields)
    
    print(f"Report Generated Successfully: {all_present}")
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    test()
