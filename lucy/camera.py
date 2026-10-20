import time
import logging

from .config import CAPTURE_SIZE, CAPTURE_PATH


def capture_image(path=CAPTURE_PATH):
    # Imported lazily so the rest of Lucy can be developed off the Pi
    from picamera2 import Picamera2

    cam = None
    try:
        cam = Picamera2()
        cam.configure(cam.create_still_configuration(main={"size": CAPTURE_SIZE}))
        cam.start()
        time.sleep(1)  # let auto-exposure settle
        cam.capture_file(path)
        logging.info("[CAMERA] Image captured.")
        return path
    except Exception as e:
        logging.error(f"[CAMERA ERROR] {e}")
        return None
    finally:
        # Without close() the next Picamera2() fails with "camera in use"
        if cam is not None:
            cam.stop()
            cam.close()
