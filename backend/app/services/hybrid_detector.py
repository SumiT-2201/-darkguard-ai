from app.services.rule_detector import RuleDetector
from app.services.ml_detector import MLDetector

class HybridDetector:
    @staticmethod
    def analyze_and_merge(html_content, text_content):
        """
        Combines rule-based and ML detection:
        - Rules for keyword/regex patterns
        - ML for semantic/linguistic patterns
        - Merges results into one deduplicated output
        """
        # 1. Rules for strong patterns
        rule_detections = RuleDetector.analyze(html_content, text_content)
        
        # 2. ML for text patterns
        ml_detections = MLDetector.predict(text_content)
        
        # 3. Merge and deduplicate results
        return HybridDetector._merge_results(rule_detections, ml_detections)

    @staticmethod
    def _merge_results(rule_detections, ml_detections):
        merged = []
        
        # Rule detections are considered grounded "strong patterns"
        merged.extend(rule_detections)
        
        # For ML detections, ensure no duplication if a rule already caught it
        for ml_det in ml_detections:
            ml_text = ml_det.get("matched_text", "").lower().strip()
            
            is_duplicate = False
            for rule_det in rule_detections:
                rule_text = rule_det.get("matched_text", "").lower().strip()
                
                # Deduplication: If rule text is part of ML sentence (or vice versa)
                # and they share the same category, keep the rule (it's more explicit)
                if (rule_text in ml_text or ml_text in rule_text) and \
                   rule_det['category'] == ml_det['category']:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(ml_det)
                
        # 4. Filter and Standardize
        filtered_results = []
        pattern_count_map = {} # Track repeated findings of same text/category
        
        for det in merged:
            method = det.get("detection_method", "")
            conf = float(det.get("confidence", 1.0))
            text = det.get("matched_text", "").lower().strip()
            category = det.get("category", "unknown")
            
            # Use improved 0.8 threshold for ML
            if method == "ml-based" and conf < 0.8:
                continue
                
            # LIMIT REPEATED FINDINGS:
            # If the same text is found multiple times for the same category, 
            # only keep the first few occurrences (max 3 per same phrase/cat)
            pattern_key = f"{category}:{text[:50]}"
            pattern_count_map[pattern_key] = pattern_count_map.get(pattern_key, 0) + 1
            if pattern_count_map[pattern_key] > 3:
                continue

            # Standardize severity based on confidence for ML
            if method == "ml-based":
                if conf >= 0.95:
                    det["severity"] = "critical"
                elif conf >= 0.85:
                    det["severity"] = "high"
                elif conf >= 0.80:
                    det["severity"] = "medium"
                else:
                    det["severity"] = "low"
                    
            filtered_results.append(det)

        # 5. Prioritize harmful patterns (Sort by severity and confidence)
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        filtered_results.sort(
            key=lambda x: (
                severity_rank.get(x.get("severity", "low").lower(), 0),
                float(x.get("confidence", 0.0))
            ),
            reverse=True
        )
                
        return filtered_results
