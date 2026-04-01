import re
from bs4 import BeautifulSoup

class RuleDetector:
    # 1. Exclusion List: Common benign UI text that should NEVER be flagged
    EXCLUSION_LIST = [
        "login", "sign up", "sign in", "new chat", "search", "menu", "home",
        "settings", "profile", "logout", "contact", "about", "help", "terms",
        "privacy", "cookies", "dashboard", "notifications", "messages",
        "create account", "forgot password", "reset password", "language",
        "search results", "back to top", "read more", "view all"
    ]

    # 2. Dictionary of Text-based Regex Rules Enhanced for broader detection
    TEXT_RULES = {
        "urgency": {
            "patterns": [
                r"only \d+ left", r"limited time", r"expires soon",
                r"deal ends", r"last chance", r"sale ends today", r"seconds to", 
                r"don't miss out", r"hurry up", r"fast-selling"
            ],
            "severity": "high",
            "explanation": "Artificial time limits put unfair psychological pressure on you to make a hasty decision."
        },
        "scarcity": {
            "patterns": [
                r"low stock", r"\d+ people have this in their cart", r"only few left",
                r"stock is low", r"while supplies last", r"limited edition", r"demand is high",
                r"popular item", r"almost gone"
            ],
            "severity": "medium",
            "explanation": "Fabricated scarcity tricks you into thinking a product is more valuable or popular than it is."
        },
        "pressure": {
            "patterns": [
                r"buy now", r"continue to proceed", r"agree to receive", r"don't wait",
                r"checkout now", r"add to cart immediately", r"unlock special offer",
                r"grab yours", r"don't let it slip"
            ],
            "severity": "medium",
            "explanation": "Aggressive language designed to steer you toward a specific action without consideration."
        },
        "hidden_cost": {
            "patterns": [
                r"additional fees", r"fees may apply", r"extra charges", r"service fee",
                r"plus handling", r"processing fee"
            ],
            "severity": "critical",
            "explanation": "Costs are hidden until the last moment, making the initial price look more attractive."
        }
    }

    @staticmethod
    def analyze(html_content, text_content):
        detections = []
        text_lower = text_content.lower()
        seen_matches = set()
        
        # --- 1. Rule-based Text Scanning ---
        for rule_type, rule_data in RuleDetector.TEXT_RULES.items():
            for pattern in rule_data["patterns"]:
                for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                    matched_text = match.group(0)
                    matched_lower = matched_text.lower().strip()
                    
                    # FALSE POSITIVE FILTER: Check against exclusion list
                    if matched_lower in RuleDetector.EXCLUSION_LIST:
                        continue
                        
                    # Contextual Filter: If the "matched text" is just a common UI word in isolation
                    if len(matched_lower.split()) < 2 and matched_lower in RuleDetector.EXCLUSION_LIST:
                        continue
                    
                    # Deduplicate exact text matches
                    if matched_lower not in seen_matches:
                        seen_matches.add(matched_lower)
                        detections.append({
                            "type": rule_type,
                            "pattern_name": rule_type.replace('_', ' ').title(),
                            "category": rule_type,
                            "matched_text": matched_text,
                            "severity": rule_data["severity"],
                            "explanation": rule_data["explanation"],
                            "detection_method": "rule-based",
                            "confidence": 1.0
                        })

        # --- 2. HTML Structure Scanning ---
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Detect Pre-selected Checkboxes (Opt-out rather than Opt-in)
            checkboxes = soup.find_all('input', type='checkbox', checked=True)
            for box in checkboxes:
                label = ""
                box_id = box.get('id')
                if box_id:
                    label_elem = soup.find('label', attrs={'for': box_id})
                    if label_elem:
                        label = label_elem.get_text(strip=True)
                
                # Exclude common benign pre-selected boxes
                if label.lower() not in ["remember me", "stay logged in", "accept terms", "i agree"]:
                    matched = label if label else "pre-selected checkbox"
                    if matched.lower() not in seen_matches:
                        seen_matches.add(matched.lower())
                        detections.append({
                            "type": "sneaking",
                            "pattern_name": "Pre-selected Checkbox",
                            "category": "sneaking",
                            "matched_text": matched[:100],
                            "severity": "medium",
                            "explanation": "A checkbox is checked by default, exploiting user inertia to gain consent automatically.",
                            "detection_method": "rule-based",
                            "confidence": 0.95
                        })

        return detections
