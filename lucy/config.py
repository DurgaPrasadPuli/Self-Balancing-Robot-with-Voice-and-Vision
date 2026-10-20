import os
import logging

from dotenv import load_dotenv

load_dotenv()

# ================= ASSISTANT =================
WAKE_WORD = os.getenv("WAKE_WORD", "lucy")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
TTS_MODEL = "eleven_turbo_v2_5"
CHAT_MODEL = "gpt-4o-mini"
VISION_MODEL = "gpt-4o"

# ================= SERIAL =================
# Prefer a /dev/serial/by-id/... path: it stays stable across reboots, unlike /dev/ttyUSB0
SERIAL_PORT = os.getenv("SERIAL_PORT")
BAUDRATE = int(os.getenv("BAUDRATE", "9600"))

# Single-byte commands understood by the balancing firmware
SERIAL_COMMANDS = {
    "BALANCE": b"5",
    "FORWARD": b"f",
    "BACK": b"b",
    "LEFT": b"l",
    "RIGHT": b"i",
    "STOP": b"s",
}

# ================= CAMERA =================
CAPTURE_SIZE = (1280, 720)
CAPTURE_PATH = "capture.jpg"

# ================= API KEYS =================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def require_config():
    required = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
        "ELEVENLABS_VOICE_ID": VOICE_ID,
        "SERIAL_PORT": SERIAL_PORT,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Missing {', '.join(missing)} in .env (see .env.example).")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(threadName)s | %(levelname)s | %(message)s",
    )
