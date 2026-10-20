import time
import logging
import threading
from queue import Queue

import serial

from .config import SERIAL_PORT, BAUDRATE, SERIAL_COMMANDS


class Robot:
    """Sends movement commands to the balancing controller over USB serial."""

    def __init__(self, port=SERIAL_PORT, baudrate=BAUDRATE):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # board resets when the port opens
            logging.info("✅ USB Serial connected.")
        except serial.SerialException as e:
            logging.error(f"[SERIAL ERROR] {e}")
            raise SystemExit(1)

        self.queue = Queue()
        threading.Thread(target=self._worker, daemon=True, name="RobotThread").start()

    def send(self, cmd):
        self.queue.put(cmd)

    def _worker(self):
        while True:
            cmd = self.queue.get()
            try:
                code = SERIAL_COMMANDS.get(cmd)
                if code:
                    self.ser.write(code)
                    logging.info(f"[ROBOT] Executed {cmd}")
                else:
                    logging.warning(f"[ROBOT] Unknown command: {cmd}")
            except Exception as e:
                logging.error(f"[ROBOT ERROR] {e}")
            finally:
                self.queue.task_done()

    def close(self):
        try:
            self.ser.write(SERIAL_COMMANDS["STOP"])
        finally:
            self.ser.close()
