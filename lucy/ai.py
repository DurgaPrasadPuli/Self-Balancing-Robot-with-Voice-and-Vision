import base64
import logging

from openai import OpenAI

from .config import OPENAI_API_KEY, CHAT_MODEL, VISION_MODEL

_client = None


def _openai():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


# ================= CHAT =================
def chat(text):
    """Return a reply to the user's question, or None on failure."""
    try:
        logging.info("[OPENAI] Processing response...")
        res = _openai().chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": text}],
        )
        reply = res.choices[0].message.content
        logging.info(f"[OPENAI] Reply: {reply}")
        return reply
    except Exception as e:
        logging.error(f"[OPENAI ERROR] {e}")
        return None


# ================= VISION =================
def encode_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"[ENCODE ERROR] {e}")
        return None


def describe_image(image_path):
    encoded = encode_image(image_path)
    if not encoded:
        return "I couldn't process the image."
    try:
        res = _openai().chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what you see in this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}},
                ],
            }],
        )
        desc = res.choices[0].message.content
        logging.info("[VISION] Description generated.")
        return desc
    except Exception as e:
        logging.error(f"[VISION ERROR] {e}")
        return "I had trouble describing the image."
