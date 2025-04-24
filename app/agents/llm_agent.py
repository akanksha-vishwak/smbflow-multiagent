# app/agents/llm_agent.py

import os
from dotenv import load_dotenv
import json
import google.generativeai as genai
import re

load_dotenv()
# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiLLMAgent:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, message: str, context: list[str], prev_info: dict | None = None) -> dict:
        prompt = self._build_prompt(message, context)

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            print("[LLMAgent] RAW Gemini output:\n", content)

            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            content = re.sub(r'//.*', '', content)
            result = json.loads(content)

            # 👇 Enforce default conversation_status if Gemini skipped it
            if "conversation_status" not in result:
                print("⚠️ Gemini did not return 'conversation_status'. Defaulting to 'continue'")
                result["conversation_status"] = "continue"

            return result

        except Exception as e:
            print("[LLMAgent] Gemini error:", e)
            return {
                "category": "unknown",
                "priority": "moderate",
                "extracted_info": {},
                "conversation_status": "continue"
            }


    def _build_prompt(self, message: str, context: list[str], prev_info: dict | None = None) -> str:
        context_str = "\n".join(f"- {msg}" for msg in context[-15:]) if context else "None"
        info_str = json.dumps(prev_info, indent=2) if prev_info else "None"

        return f"""
    You are a smart assistant for WhatsApp conversations between businesses and their customers.

    You will be given:
    - Previous structured order/extraction data
    - Context of recent messages
    - A new message

    Your job is to intelligently **update the extracted_info** based on the new message.
    If the message adds or updates products, addresses, delivery methods, etc., reflect that.
    If it says something irrelevant like "thanks", the extracted_info should remain unchanged.

    ---

    Previous extracted_info:
    {info_str}

    Context:
    {context_str}

    New Message:
    "{message}"

    Return updated extracted_info as JSON.

    Also return:
    - category
    - priority
    - conversation_status

    Response format:
    {{
    "category": "update",
    "priority": "moderate",
    "conversation_status": "continue",
    "extracted_info": {{
        ...
    }}
    }}
        """.strip()
