import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ContextFilterAgent:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        self.model = genai.GenerativeModel(model_name)

    def filter_context(self, history: list[str], new_message: str) -> list[str]:
        prompt = self._build_prompt(history, new_message)

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()

            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            return eval(content) if isinstance(content, str) else content
        except Exception as e:
            print("[ContextFilterAgent] ❌ Error:", e)
            return history[-3:]  # fallback: last 3 messages

    def _build_prompt(self, history, new_message) -> str:
        history_block = "\n".join(f"- {m}" for m in history[-10:])

        return f"""
You are a smart assistant helping a business analyze messages.

Here is the conversation history:
{history_block}

New customer message:
"{new_message}"

Select only the relevant messages from the history that are important for understanding or responding to this new message.

Return your answer as a JSON list of strings. Only include messages that directly support or relate to the new message.
""".strip()


context_filter_agent = ContextFilterAgent()
