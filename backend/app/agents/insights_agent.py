import json
from google import genai
from app.core.config import settings

class InsightsAgent:
    @staticmethod
    async def generate_insights(spend_data: list[dict]):
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
            Analyze the following spend data and provide business insights:
            Data: {json.dumps(spend_data)}
            
            Please provide:
            1. Monthly Spending Trends
            2. Vendor Concentration Analysis
            3. Cost Forecasting
            4. Anomaly Detection
            
            Return ONLY a valid JSON object containing these keys. Do not use markdown.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            extracted_text = response.text.strip()
            if extracted_text.startswith("```json"):
                extracted_text = extracted_text.replace("```json", "").replace("```", "").strip()
                
            return json.loads(extracted_text)
        except Exception as e:
            return {"error": str(e)}
