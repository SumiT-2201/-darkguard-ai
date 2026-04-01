from datetime import datetime
from urllib.parse import urlparse

class ReportGenerator:
    @staticmethod
    def _generate_recommendations(unique_patterns, score_data):
        recommendations = []
        categories_found = set(p['category'].lower() for p in unique_patterns)
        
        # General Recommendations based on score
        if score_data['trust_score'] >= 90:
            recommendations.append({
                "title": "Stay Vigilant",
                "description": "The website appears trustworthy, but always review terms before large transactions."
            })
        elif score_data['trust_score'] < 70:
             recommendations.append({
                "title": "High Risk Detected",
                "description": "Multiple deceptive patterns found. We recommend avoiding this site for sensitive transactions."
            })

        # Category-specific Recommendations
        if any(c in categories_found for c in ["fake_urgency", "urgency"]):
            recommendations.append({
                "title": "Verify Urgency",
                "description": "Don't rush based on countdown timers or 'limited stock' labels. Verify if the deal is actually expiring by refreshing the page or checking elsewhere."
            })
            
        if "hidden_costs" in categories_found:
            recommendations.append({
                "title": "Check Final Total",
                "description": "Before clicking 'Pay', ensure the total matches the advertised price. Watch for 'service fees' or 'convience fees' added at the last second."
            })
            
        if any(c in categories_found for c in ["forced_actions", "forced_action"]):
            recommendations.append({
                "title": "Protect Your Data",
                "description": "If asked to sign up just to 'see a price' or 'read an article', try using a throwaway email or looking for the information on a less restrictive site."
            })
            
        if any(c in categories_found for c in ["confirm_shaming", "misdirection", "misleading_button"]):
            recommendations.append({
                "title": "Read Carefully",
                "description": "Don't let guilt-tripping language (e.g., 'No, I prefer to pay more') influence your choice. Focus on the actual function of the buttons, not the labels."
            })
            
        if "sneaking" in categories_found or "pre_selected_checkbox" in categories_found:
            recommendations.append({
                "title": "Inspect Checkboxes",
                "description": "Always scroll through the entire page during checkout to ensure no 'add-on' services or 'newsletter' subscriptions are pre-selected for you."
            })
            
        # Default recommendation if none matched
        if not recommendations:
            recommendations.append({
                "title": "General Safety",
                "description": "Always use secure payment methods and avoid saving credit card details on unfamiliar websites."
            })
            
        return recommendations

    @staticmethod
    def build_report(url, meta, score_data, patterns):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Deduplicate patterns
        unique_patterns = []
        seen = set()
        for p in patterns:
            key = f"{p['category']}-{p['matched_text']}"
            if key not in seen:
                seen.add(key)
                unique_patterns.append(p)
        
        grade_labels = {
            "A": "Excellent - No dark patterns detected",
            "B": "Good - Minor deceptive practices",
            "C": "Fair - Several dark patterns present",
            "D": "Poor - High risk of deceptive UX",
            "F": "Critical - Predatory patterns detected"
        }
        
        # Grouped categories for summary
        categories_summary = {}
        for p in unique_patterns:
            cat = p['category'].replace('_', ' ').title()
            categories_summary[cat] = categories_summary.get(cat, 0) + 1
        
        categories_list = [{"name": name, "count": count} for name, count in categories_summary.items()]
        recommendations = ReportGenerator._generate_recommendations(unique_patterns, score_data)
        
        # The user requested specific JSON fields: Trust score, Findings list, Categories, Recommendations
        return {
            "url": url,
            "domain": domain,
            "scan_date": datetime.utcnow().isoformat(),
            "meta": {
                "title": meta.get('title', 'Unknown'),
                "description": meta.get('description', 'No description available')
            },
            "trust_score": score_data['trust_score'],
            "grade": score_data['grade'],
            "grade_explanation": grade_labels.get(score_data['grade'], "Unknown"),
            "severity_breakdown": score_data['severity_counts'],
            "findings_list": unique_patterns,
            "categories": categories_list,
            "recommendations": recommendations,
            "summary_text": f"Detected {len(unique_patterns)} distinctive dark patterns across {len(categories_list)} categories. " 
                           f"The overall trust score for {domain} is {score_data['trust_score']}/100."
        }
