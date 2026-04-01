class ScoreEngine:
    @staticmethod
    def calculate_trust_score(detections):
        """
        Calculates a realistic trust score with capped deductions.
        Fixed Deductions:
        low → -5 | medium → -10 | high → -20 | critical → -30
        
        Logic:
        - Deduplicate findings by text and category before scoring.
        - Limit repeated category penalties (diminishing returns).
        - Max penalty capped at 50 (unless >3 high/critical patterns exist).
        """
        base_score = 100
        total_deduction = 0
        
        severity_mapping = {
            "critical": 30,
            "high": 20,
            "medium": 12,
            "low": 5
        }
        
        # 1. DEDUPLICATE: Ensure we only score unique text/category pairs
        unique_detections = []
        seen = set()
        for d in detections:
            key = f"{d.get('category')}:{d.get('matched_text', '').lower().strip()}"
            if key not in seen:
                seen.add(key)
                unique_detections.append(d)
        
        # 2. CATEGORY PENALTY LIMITS: Prevent alert spamming for same pattern type
        category_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for d in unique_detections:
            sev = d.get('severity', 'low').lower()
            cat = d.get('category', 'unknown').lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            # Diminishing returns within the same category:
            # 1st pattern: 100% deduction
            # 2nd pattern: 25% deduction
            # 3rd+ pattern: 0% deduction
            current_cat_count = category_counts.get(cat, 0) + 1
            category_counts[cat] = current_cat_count
            
            base_deduction = severity_mapping.get(sev, 5)
            if current_cat_count == 1:
                deduction = base_deduction
            elif current_cat_count == 2:
                deduction = base_deduction * 0.25
            else:
                deduction = 0
                
            total_deduction += deduction

        # 3. CAPPING LOGIC (Max 50 pts deduction)
        # "Minimum score = 50 unless strong patterns exist"
        # Strong patterns = more than 3 high/critical unique items
        strong_pattern_count = severity_counts.get('critical', 0) + severity_counts.get('high', 0)
        
        if strong_pattern_count < 3:
            total_deduction = min(50, total_deduction)
        else:
            # If strong patterns exist, allows score to drop below 50, but still capped at 90 total deduction
            total_deduction = min(90, total_deduction)

        # 4. Final Final Score (min 10 since no site is totally 0 unless predatory)
        trust_score = round(max(10, base_score - total_deduction))
        
        # Aggregate categories for frontend
        agg_categories = {}
        for d in unique_detections:
            cat = d.get('category' or 'type' or 'miscellaneous').lower()
            cat_name = cat.replace('_', ' ').replace('-', ' ').title()
            if cat not in agg_categories:
                agg_categories[cat] = {"name": cat_name, "count": 0}
            agg_categories[cat]["count"] += 1

        # Grades (A: 90+, B: 80+, C: 70+, D: 50+, F: <50)
        if trust_score >= 90: grade = "A"
        elif trust_score >= 80: grade = "B"
        elif trust_score >= 70: grade = "C"
        elif trust_score >= 50: grade = "D"
        else: grade = "F"
            
        return {
            "trust_score": trust_score,
            "grade": grade,
            "severity_counts": severity_counts,
            "categories": list(agg_categories.values())
        }
