"""
Shared helpers for parsing JSON from Gemini text responses.
"""
import json


def parse_json_from_model_text(raw_text: str) -> dict:
    """
    Strip markdown fences and extract the outermost JSON object from model output.
    Raises json.JSONDecodeError on failure.
    """
    if not raw_text or not raw_text.strip():
        raise json.JSONDecodeError("Empty model response", "", 0)

    text = raw_text.strip()

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    return json.loads(text)
