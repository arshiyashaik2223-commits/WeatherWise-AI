"""Optional hosted AI explanation layer; deterministic analysis remains the source of truth."""
import os
import json

def explain_with_ai(question: str, computed_context: dict, provider: str | None=None) -> str:
    provider=(provider or os.getenv("WEATHERWISE_AI_PROVIDER","anthropic")).lower()
    # Context is computed by the app; model is instructed not to invent values.
    context=json.dumps(computed_context, default=str)[:12000]
    if provider == "anthropic":
        key=os.getenv("ANTHROPIC_API_KEY")
        if not key: raise RuntimeError("AI API key not configured. Local Pandas assistant is still available.")
        try:
            import anthropic
            client=anthropic.Anthropic(api_key=key)
            response=client.messages.create(model=os.getenv("ANTHROPIC_MODEL","claude-3-5-haiku-latest"),max_tokens=700,system="Explain only the supplied computed dataset context. Do not invent measurements, dates, forecasts, or unsupported conclusions. If context is insufficient, say so. Historical observations are not forecasts.",messages=[{"role":"user","content":f"Question: {question}\nComputed dataset context (JSON): {context}"}])
            return "".join(getattr(block,"text","") for block in response.content)
        except ImportError as exc: raise RuntimeError("Install the optional anthropic package to enable hosted AI.") from exc
    if provider == "openai":
        key=os.getenv("OPENAI_API_KEY")
        if not key: raise RuntimeError("OPENAI_API_KEY is not configured. Local Pandas assistant is still available.")
        try:
            from openai import OpenAI
            response=OpenAI(api_key=key).chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),messages=[{"role":"system","content":"Explain only supplied computed dataset context. Never invent data or present historical observations as forecasts."},{"role":"user","content":f"Question: {question}\nComputed context: {context}"}],max_tokens=700)
            return response.choices[0].message.content or "No explanation returned."
        except ImportError as exc: raise RuntimeError("Install the optional openai package to enable hosted AI.") from exc
    raise ValueError("Unsupported provider. Choose 'anthropic' or 'openai'.")
