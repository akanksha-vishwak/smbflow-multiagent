from app.agents.llm_agent import GeminiLLMAgent
from app.agents.memory_agent import memory_agent
from app.state import MessageState
import json

# Initialize Gemini LLM agent
llm_agent = GeminiLLMAgent()


def llm_node(state: MessageState) -> MessageState:
    if not state.message:
        print("[LLMNode] ⚠️ No message to analyze")
        return state

    print(f"[LLMNode] 🤖 Analyzing message: {state.message}")

    # === Load long-term structured memory ===
    prev_info = memory_agent.get_last_extracted_info(state.customer_id)
    print("[LLMNode] 🧠 Previous structured info:\n", json.dumps(prev_info, indent=2))

    # === Run LLM with message, context, and prior memory ===
    result = llm_agent.analyze(
        message=state.message,
        context=state.context,
        prev_info=prev_info
    )

    # === Update the state with LLM results ===
    state.predicted_category = result.get("category", "unknown")
    state.priority = result.get("priority", "moderate")
    state.conversation_status = result.get("conversation_status", "continue")
    state.extracted_info = result.get("extracted_info", {})

    print(f"[LLMNode] ✅ Analysis result:\n{json.dumps(result, indent=2)}")
    print(f"[LLMNode] 🧾 Final extracted_info:\n{json.dumps(state.extracted_info, indent=2)}")

    # === Persist updated extracted info to memory ===
    memory_agent.update_extracted_info(state.customer_id, state.extracted_info)

    # (Optional) Save message to history
    memory_agent.append_to_history(state.customer_id, state.message)

    return state
