# Self-Balancing Robot — "Lucy"

Voice- and vision-controlled self-balancing robot. A Raspberry Pi runs **Lucy**, which:

- listens for the wake word **"Lucy"**,
- turns spoken commands into movement commands sent over USB serial to the balancing controller (Arduino / CH340 board),
- takes a photo with the Pi camera and describes it (OpenAI vision),
- answers anything else with OpenAI chat, and speaks every reply with ElevenLabs.

## Project layout

```
main.py             entry point / main loop
lucy/
  config.py         settings, serial command map, env loading
  robot.py          serial link + command queue worker
  speech.py         ElevenLabs TTS, speech recognition, wake-word listener
  ai.py             OpenAI chat + image description
  camera.py         Pi camera capture
  commands.py       maps spoken phrases to actions
```

## Voice commands

Say "Lucy", wait for "Yes?", then:

| Say                          | Action  | Serial byte |
|------------------------------|---------|-------------|
| "stop" (checked first)       | STOP    | `s`         |
| "balance"                    | BALANCE | `5`         |
| "move forward" / "go forward"| FORWARD | `f`         |
| "move back" / "go back"      | BACK    | `b`         |
| "turn left"                  | LEFT    | `l`         |
| "turn right"                 | RIGHT   | `i`         |
| "see" / "look" / "photo" / "picture" | Describe what the camera sees | – |
| anything else                | Chat reply | – |

The firmware on the balancing board must accept these single-byte commands at 9600 baud.

## Setup (Raspberry Pi OS)

```bash
sudo apt install python3-picamera2 ffmpeg alsa-utils portaudio19-dev flac
python3 -m venv --system-site-packages venv   # system site-packages for picamera2
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # then fill in your keys, voice ID and serial port
python main.py
```

Set `SERIAL_PORT` in `.env` to your board's path. Run `ls /dev/serial/by-id/` to find it.
