import anthropic
import json
import logging
from app.config import Config

class LlmDetector:
    client = None
    
    @classmethod
    def get_client(cls):
        if cls.client is None and Config.CLAUDE_API_KEY != 'your-api-key-here':
            try:
                cls.client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
            except Exception as e:
                logging.error(f"Failed to initialize Anthropic client: {e}")
        return cls.client

    @staticmethod
    def analyze_text(text_content):
        """
        Uses Claude LLM for semantic dark pattern detection.
        Catches subtle patterns (scarcity, urgency, forced action, etc.) 
        that regex might miss.
        """
        client = LlmDetector.get_client()
        if not client:
            return None # Falls back to regex in HybridDetector

        # System prompt to define the detection persona
        system_prompt = """
        You are a specialist in deceptive UI/UX practices (dark patterns). 
        Your task is to analyze UI text fragments and determine if they are manipulative.
        Target patterns:
        - Urgency: High pressure, short timers.
        - Scarcity: "Only 2 left", "others looking".
        - Social Proof: "Join 10k users", "just bought in London".
        - Forced Action: "Join to unlock", "marketing agree to continue".
        - Hidden Cost: "Unannounced fees", "taxes calculated later".

        Format your output EXACTLY as a JSON object: 
        { "is_dark_pattern": bool, "category": string or "none", "confidence": float, "reason": string }
        """
        
        user_prompt = f"Analyze this UI text: '{text_content}'"
        
        try:
            # Using the requested model ID (claude-3-5-sonnet-20241022 as fallback if futuristic ID fails in current sdk)
            model_to_use = "claude-3-5-sonnet-20241022" 
            
            message = client.messages.create(
                model=model_to_use,
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse response
            res_content = message.content[0].text
            res_json = json.loads(res_content)
            
            # Filter by confidence threshold (Config.LLM_CONFIDENCE_THRESHOLD)
            if res_json.get("confidence", 0) < Config.LLM_CONFIDENCE_THRESHOLD:
                return None
                
            if not res_json.get("is_dark_pattern", False):
                return None
                
            return {
                "pattern_name": f"AI Prediction ({res_json['category'].replace('_', ' ').title()})",
                "category": res_json['category'].lower(),
                "matched_text": text_content,
                "severity": "high" if res_json.get("confidence", 0) > 0.9 else "medium",
                "explanation": res_json.get("reason", "Detected by Claude AI analysis."),
                "detection_method": "llm-based",
                "confidence": res_json.get("confidence", 0.0)
            }
            
        except Exception as e:
            logging.error(f"LLM Detection Error: {e}")
            return None
