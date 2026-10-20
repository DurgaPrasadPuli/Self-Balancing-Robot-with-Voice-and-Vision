import time
import logging
import threading

from lucy.config import require_config, setup_logging
from lucy.robot import Robot
from lucy.speech import speak, listen_blocking, start_wake_listener
from lucy.commands import handle_command


def main():
    setup_logging()
    require_config()

    robot = Robot()
    wake_event = threading.Event()

    speak("Lucy is online.")
    stop_listening = start_wake_listener(wake_event)

    try:
        while True:
            wake_event.wait()
            wake_event.clear()
            speak("Yes?")
            cmd = listen_blocking(timeout=5, phrase_limit=6)
            handle_command(cmd, robot)
            time.sleep(0.2)
    except KeyboardInterrupt:
        logging.info("[SYSTEM] Exiting via KeyboardInterrupt")
    finally:
        stop_listening(wait_for_stop=False)
        robot.close()
        speak("Goodbye.")
        logging.info("[SYSTEM] Lucy offline.")


if __name__ == "__main__":
    main()
