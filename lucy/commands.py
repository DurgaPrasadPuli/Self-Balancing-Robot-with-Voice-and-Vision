import logging
import threading

from .ai import chat, describe_image
from .camera import capture_image
from .speech import speak

VISION_WORDS = ("see", "look", "photo", "picture")


def _chat_and_speak(text):
    reply = chat(text)
    speak(reply if reply else "I had trouble answering that.")


def handle_command(cmd, robot):
    logging.info(f"[HANDLE] {cmd}")
    if not cmd:
        return

    # Stop is checked first so "stop balancing" never starts the motors
    if "stop" in cmd:
        robot.send("STOP")
        speak("Stopping")
    elif "balance" in cmd:
        speak("Balancing")
        robot.send("BALANCE")
    elif "move forward" in cmd or "go forward" in cmd:
        speak("Moving forward")
        robot.send("FORWARD")
    elif "move back" in cmd or "go back" in cmd:
        speak("Moving backward")
        robot.send("BACK")
    elif "turn left" in cmd:
        speak("Turning left")
        robot.send("LEFT")
    elif "turn right" in cmd:
        speak("Turning right")
        robot.send("RIGHT")
    elif any(word in cmd for word in VISION_WORDS):
        speak("Let me take a look.")
        img_path = capture_image()
        speak(describe_image(img_path) if img_path else "I couldn't take a picture.")
    else:
        threading.Thread(target=_chat_and_speak, args=(cmd,), daemon=True, name="ChatThread").start()
