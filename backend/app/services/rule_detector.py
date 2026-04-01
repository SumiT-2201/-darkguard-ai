import re
from bs4 import BeautifulSoup

class RuleDetector:
    # 1. Exclusion List: Common benign UI text that should NEVER be flagged
    EXCLUSION_LIST = [
        "login", "sign up", "sign in", "new chat", "search", "menu", "home",
        "settings", "profile", "logout", "contact", "about", "help", "terms",
        "privacy", "cookies", "dashboard", "notifications", "messages",
        "create account", "forgot password", "reset password", "language",
        "search results", "back to top", "read more", "view all", "copyright",
        "all rights reserved", "powered by", "facebook", "twitter", "instagram",
        "linkedin", "youtube", "social media", "site map", "go to top"
    ]

    # 2. Dictionary of Text-based Regex Rules: Refined for STRONGER persuasive language
    TEXT_RULES = {
        "urgency": {
            "patterns": [
                r"only \d+ items? left in stock", 
                r"limited time offer expires soon",
                r"hurry up! deal ends in \d+ minutes", 
                r"act now and save",
                r"last chance to grab this deal",
                r"one-time offer",
                r"seconds to go before price increases"
            ],
            "severity": "high",
            "explanation": "Artificial time limits put unfair psychological pressure on you to make a hasty decision."
        },
        "scarcity": {
            "patterns": [
                r"\d+ people have this in their cart right now",
                r"low stock - almost sold out",
                r"only few items left at this price",
                r"high demand - while supplies last",
                r"limited edition item",
                r"join \d+ others waiting for this"
            ],
            "severity": "medium",
            "explanation": "Fabricated scarcity tricks you into thinking a product is more valuable or popular than it is."
        },
        "pressure": {
            "patterns": [
                r"buy now and get a bonus",
                r"continue to proceed to checkout",
                r"agree to receive promotional offers",
                r"grab yours before it's gone",
                r"unlock your special offer immediately",
                r"don't let this item slip away"
            ],
            "severity": "medium",
            "explanation": "Aggressive language designed to steer you toward a specific action without consideration."
        },
        "hidden_cost": {
            "patterns": [
                r"additional costs and fees will be added",
                r"service fees and taxes not included",
                r"extra charges added at checkout",
                r"processing fee of \d+ will be applied"
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
                    word_count = len(matched_lower.split())
                    
                    # FALSE POSITIVE FILTERS
                    # A. Exclusion list check
                    if matched_lower in RuleDetector.EXCLUSION_LIST:
                        continue
                        
                    # B. Minimum Phrase Length (>5 words) as requested
                    # Only apply to general pattern matches, not extremely specific ones
                    if word_count <= 5 and matched_lower not in ["only 1 left", "low stock"]:
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
            
            # Detect Pre-selected Checkboxes
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
