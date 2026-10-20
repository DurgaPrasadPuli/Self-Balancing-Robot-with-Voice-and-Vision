import os
import logging
import tempfile
import threading
import subprocess

import speech_recognition as sr
from elevenlabs.client import ElevenLabs

from .config import ELEVENLABS_API_KEY, VOICE_ID, TTS_MODEL, WAKE_WORD

# Held while Lucy is talking so the microphone ignores her own voice
audio_lock = threading.Lock()

recognizer = sr.Recognizer()
recognizer.energy_threshold = 400
recognizer.dynamic_energy_threshold = True

_tts = None


def _tts_client():
    global _tts
    if _tts is None:
        _tts = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _tts


# ================= TEXT-TO-SPEECH =================
def speak(text):
    logging.info(f"Lucy: {text}")
    try:
        audio = _tts_client().text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id=TTS_MODEL,
            output_format="mp3_44100_128",
        )

        # Per-call temp files: chat replies speak from another thread
        with tempfile.TemporaryDirectory() as tmp:
            tmp_mp3 = os.path.join(tmp, "response.mp3")
            tmp_wav = os.path.join(tmp, "response.wav")

            with open(tmp_mp3, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            with audio_lock:
                subprocess.run(
                    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp_mp3, "-ar", "48000", tmp_wav],
                    check=True,
                )
                subprocess.run(["aplay", "-q", tmp_wav], check=False)

    except Exception as e:
        logging.error(f"[TTS ERROR] {e}")


# ================= LISTEN FOR COMMAND =================
def listen_blocking(timeout=None, phrase_limit=5):
    if audio_lock.locked():
        return None

    with sr.Microphone() as source:
        logging.info("🎤 Listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio).lower()
            logging.info(f"[USER COMMAND] {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            logging.info("[LISTEN] No valid input.")
            return None
        except sr.RequestError as e:
            logging.error(f"[LISTEN ERROR] {e}")
            return None


# ================= WAKE WORD LISTENER =================
def start_wake_listener(wake_event):
    """Listen in the background and set wake_event when the wake word is heard.

    Returns the function that stops the listener.
    """

    def wake_callback(recognizer_, audio):
        if audio_lock.locked():
            return
        try:
            text = recognizer_.recognize_google(audio).lower()
            if WAKE_WORD in text:
                logging.info("[WAKE] Wake word detected.")
                wake_event.set()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            logging.error(f"[BACKGROUND ERROR] {e}")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    stop_listening = recognizer.listen_in_background(sr.Microphone(), wake_callback)
    logging.info("[SYSTEM] Background listener started.")
    return stop_listening
