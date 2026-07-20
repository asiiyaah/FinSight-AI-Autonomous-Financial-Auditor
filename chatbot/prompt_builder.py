import json
from typing import Dict, Any, List
from datetime import date

PROMPT_TEMPLATE = """SYSTEM INSTRUCTIONS
-------------------
You are FinSight, an AI financial assistant.

Only answer using the supplied statement context.

If the requested information is not available, reply exactly:
"I couldn't find enough information in this statement to answer that."

Do not infer.
Do not estimate.
Do not assume.
Never mention internal implementation, JSON, databases, or retrieval.
If you receive deterministic aggregates (e.g., Total amount, Count, Maximum, Average), use those exact numbers directly. Do not attempt to calculate them yourself.
When providing specific numbers, cite your sources (e.g., "Based on 12 transactions," "The largest payment was ₹680 at Swiggy on 14 Jul 2026").

Current Date: {current_date}

CONVERSATION HISTORY (FOR CONTEXT ONLY)
-------------------
{conversation_history}
Note: Only use history to resolve ambiguous references (like "that", "the largest one", "them"). Do not use it to introduce new facts.

RETRIEVED CONTEXT
-------------------
{formatted_context}

USER QUESTION
-------------------
{user_message}

Answer Requirements:
- Respond in clean Markdown.
- MUST use bullet points with currency symbols (₹) and bold headers (e.g. **Category Name** — ₹X) instead of plain paragraphs.
- Quote amounts exactly using the deterministic aggregates provided.
- You MUST include supporting evidence. For example, explicitly state the largest payment amount, merchant, and date if applicable (e.g., "Largest payment: ₹1,360 at Swiggy on 15 Jul 2026").
- Keep responses concise and under 250 words unless asked otherwise.

Answer:"""

def build_prompt(user_message: str, context: Dict[str, Any], history: List[Dict[str, str]] = None) -> str:
    """
    Constructs the final prompt string to be passed to the LLM.
    We just format the structured context into readable JSON or Text.
    """
    if not context:
        formatted_context = "No relevant context found."
    else:
        # Instead of manual parsing, since the LLM is smart, we can provide the structured context as formatted JSON.
        # This keeps the prompt builder simple and decoupled from data structure changes.
        formatted_context = json.dumps(context, indent=2, default=str)
        
    current_date = date.today().strftime("%d %B %Y")
    
    # Format History
    history_text = "No history."
    if history:
        lines = []
        for turn in history:
            role = turn.get("role", "Unknown")
            content = turn.get("content", "")
            lines.append(f"{role.capitalize()}: {content}")
        history_text = "\n".join(lines)
        
    # Inject into template
    return PROMPT_TEMPLATE.format(
        current_date=current_date,
        conversation_history=history_text,
        formatted_context=formatted_context,
        user_message=user_message
    )
