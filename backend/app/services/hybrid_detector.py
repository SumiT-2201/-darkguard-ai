from app.services.rule_detector import RuleDetector
from app.services.ml_detector import MLDetector
from app.services.llm_detector import LlmDetector

class HybridDetector:
    @staticmethod
    def analyze_and_merge(html_content, text_content):
        """
        Combines rule-based, ML, and LLM detection:
        - Rules for keyword/regex (grounded/fast)
        - ML for high-confidence text classification (efficient/local)
        - LLM for semantic, complex, or subtle patterns (sophisticated/cloud)
        """
        # 1. Start with Rules and ML (fast/reliable base)
        rule_detections = RuleDetector.analyze(html_content, text_content)
        ml_detections = MLDetector.predict(text_content)
        
        # 2. Add LLM Analysis for complex semantic patterns (Claude API)
        # We only call LLM if it's configured and potentially can catch subtle ones.
        # But to be efficient, we only call LLM on a subset of phrases or the whole content.
        # Here we'll try to find more detections with LLM
        llm_detections = []
        sentences = text_content.split(' | ')
        
        # To avoid massive API costs/latency, we only scan suspicious sentences specifically with LLM
        # Or those missed by Rule/ML but still look like "pattern" language.
        # For this task, we'll try to call LLM on a few key segments.
        for sent in sentences[:15]: # Limit to first 15 segments for performance
            if len(sent.split()) > 4: # Only check significant phrases
                llm_det = LlmDetector.analyze_text(sent)
                if llm_det:
                    llm_detections.append(llm_det)
        
        # 3. Merge results into one deduplicated output
        return HybridDetector._merge_results(rule_detections, ml_detections, llm_detections)

    @staticmethod
    def _merge_results(rule_detections, ml_detections, llm_detections):
        merged = []
        
        # Add Rules and ML results first
        merged.extend(rule_detections)
        merged.extend(ml_detections)
        
        # For LLM detections, ensure we don't duplicate if a rule/ml already caught it
        # However, LLM is "higher authority" for reasons/explanation.
        for llm_det in llm_detections:
            llm_text = llm_det.get("matched_text", "").lower().strip()
            
            is_duplicate = False
            for existing_det in merged:
                existing_text = existing_det.get("matched_text", "").lower().strip()
                if existing_text in llm_text or llm_text in existing_text:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(llm_det)

        # Apply filtering, deduplication, and severity ranking (Same as before)
        filtered_results = []
        pattern_count_map = {} 
        
        for det in merged:
            method = det.get("detection_method", "")
            conf = float(det.get("confidence", 1.0))
            text = det.get("matched_text", "").lower().strip()
            category = det.get("category", "unknown")
            
            # Already handled LLM confidence in LlmDetector, but double check others
            if method == "ml-based" and conf < 0.8:
                continue
                
            pattern_key = f"{category}:{text[:50]}"
            pattern_count_map[pattern_key] = pattern_count_map.get(pattern_key, 0) + 1
            if pattern_count_map[pattern_key] > 3:
                continue

            filtered_results.append(det)

        # Prioritize harmful patterns (Sort by severity and confidence)
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        filtered_results.sort(
            key=lambda x: (
                severity_rank.get(x.get("severity", "low").lower(), 0),
                float(x.get("confidence", 0.0))
            ),
            reverse=True
        )
                
        return filtered_results
