class ScoreEngine:
    @staticmethod
    def calculate_trust_score(detections):
        """
        Calculates a realistic trust score with capped deductions.
        Fixed Deductions:
        low → -5 | medium → -10 | high → -20 | critical → -30
        
        Logic:
        - Max deduction capped at 50 (unless very many patterns exist)
        - Final score results in min 50 for websites with moderate noise
        """
        base_score = 100
        total_deduction = 0
        
        severity_mapping = {
            "critical": 30,
            "high": 20,
            "medium": 12,
            "low": 5
        }
        
        severity_counts = {
            "critical": 0, "high": 0, "medium": 0, "low": 0
        }
        
        for d in detections:
            sev = d.get('severity', 'low').lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            total_deduction += severity_mapping.get(sev, 5)
            
        # CAPPING LOGIC (Max 50 pts deduction for first few offenses)
        # Allows for a "noisy" site to still maintain a "D" grade (Fairly safe)
        if total_deduction > 50:
             # Gradual deduction beyond 50
             extra = (total_deduction - 50) * 0.5
             total_deduction = 50 + extra
        
        # Determine strictness: If only 1-2 weak patterns, don't penalize heavily
        if len(detections) <= 1 and total_deduction > 0:
            total_deduction = total_deduction * 0.5

        trust_score = round(max(0, base_score - total_deduction))
        
        # Aggregate findings info
        agg_categories = {}
        for d in detections:
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
