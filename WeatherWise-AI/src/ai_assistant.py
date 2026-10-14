
"""Optional hosted AI explanation layer; local analysis remains the source of truth."""

import os
import json


def explain_with_ai(
    question: str,
    computed_context: dict,
    provider: str | None = None,
) -> str:
    provider = (
        provider or os.getenv("WEATHERWISE_AI_PROVIDER", "anthropic")
    ).lower()

    # Context is computed by the app; the model must not invent values.
    context = json.dumps(computed_context, default=str)[:12000]

    if provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")

        if not key:
            return (
                "🌦️ Local AI Mode\n\n"
                "Your answer is based on calculations from your "
                "currently loaded dataset using Pandas."
            )

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=key)
            response = client.messages.create(
                model=os.getenv(
                    "ANTHROPIC_MODEL", "claude-3-5-haiku-latest"
                ),
                max_tokens=700,
                system=(
                    "Explain only the supplied computed dataset context. "
                    "Do not invent measurements, dates, forecasts, or "
                    "unsupported conclusions. If context is insufficient, "
                    "say so. Historical observations are not forecasts."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n"
                            f"Computed dataset context (JSON): {context}"
                        ),
                    }
                ],
            )
            return "".join(
                getattr(block, "text", "")
                for block in response.content
            )

        except ImportError:
            return (
                "Hosted AI is unavailable because the optional "
                "'anthropic' package is not installed. "
                "Local Pandas analysis remains available."
            )

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")

        if not key:
            return (
                "🌦️ Local AI Mode\n\n"
                "Your answer is based on calculations from your "
                "currently loaded dataset using Pandas."
            )

        try:
            from openai import OpenAI

            response = OpenAI(api_key=key).chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain only supplied computed dataset "
                            "context. Never invent data or present "
                            "historical observations as forecasts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n"
                            f"Computed context: {context}"
                        ),
                    },
                ],
                max_tokens=700,
            )
            return (
                response.choices[0].message.content
                or "No explanation returned."
            )

        except ImportError:
            return (
                "Hosted AI is unavailable because the optional "
                "'openai' package is not installed. "
                "Local Pandas analysis remains available."
            )

    return (
        "🌦️ Local AI Mode\n\n"
        "Your answer is calculated from the currently loaded "
        "dataset using Pandas."
    )
