import sounddevice as sd
import json
import queue
import requests
import time

from vosk import Model, KaldiRecognizer
from motor_driver import forward, backward, left, right, stop

# ------------------------------
# SETTINGS
# ------------------------------

WAKE_PHRASE = ["hey sonu", "hey son"]
LLM_URL = "http://192.168.1.8:11434/api/generate"
MODEL_NAME = "phi3:mini"

CONTINUOUS_MODE = False
CURRENT_DIRECTION = None

# ------------------------------
# LOAD VOSK MODEL
# ------------------------------

model = Model("model")
rec = KaldiRecognizer(model, 16000)
audio_q = queue.Queue()

def callback(indata, frames, time, status):
    audio_q.put(bytes(indata))

stream = sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
)

# ------------------------------
def listen():
    """Listen for speech and return recognized text."""
    while True:
        data = audio_q.get()
        if rec.AcceptWaveform(data):
            text = rec.Result()
            try:
                t = json.loads(text)["text"]
                return t.lower()
            except:
                return ""
        else:
            partial = rec.PartialResult()
            try:
                t = json.loads(partial)["partial"]
                return t.lower()
            except:
                return ""

# ------------------------------
def chat_with_llm(text):
    payload = {
        "model": MODEL_NAME,
        "prompt": text
    }
    r = requests.post(LLM_URL, json=payload, timeout=20)
    return r.json().get("response", "")

# ------------------------------
def continuous_move():
    """Handles continuous movement based on CURRENT_DIRECTION."""
    global CONTINUOUS_MODE, CURRENT_DIRECTION
    print("Sonu: Continuous mode activated:", CURRENT_DIRECTION)

    while CONTINUOUS_MODE:
        if CURRENT_DIRECTION == "forward":
            forward(0.2)
        elif CURRENT_DIRECTION == "backward":
            backward(0.2)
        elif CURRENT_DIRECTION == "left":
            left(0.2)
        elif CURRENT_DIRECTION == "right":
            right(0.2)

        # small delay between loops
        time.sleep(0.1)

# ------------------------------
def handle_command(cmd):
    """Parse user command."""
    global CONTINUOUS_MODE, CURRENT_DIRECTION

    # STOP continuous mode
    if "stop" in cmd:
        CONTINUOUS_MODE = False
        CURRENT_DIRECTION = None
        stop()
        print("Sonu: Stopped.")
        return

    # CONTINUOUS MOVEMENT
    if "continue forward" in cmd:
        CURRENT_DIRECTION = "forward"
        CONTINUOUS_MODE = True
        continuous_move()
        return

    if "continue back" in cmd:
        CURRENT_DIRECTION = "backward"
        CONTINUOUS_MODE = True
        continuous_move()
        return

    if "continue left" in cmd:
        CURRENT_DIRECTION = "left"
        CONTINUOUS_MODE = True
        continuous_move()
        return

    if "continue right" in cmd:
        CURRENT_DIRECTION = "right"
        CONTINUOUS_MODE = True
        continuous_move()
        return

    # NORMAL MOVEMENT
    if "forward" in cmd:
        print("Sonu: Moving forward.")
        forward()
        return

    if "back" in cmd:
        print("Sonu: Moving backward.")
        backward()
        return

    if "left" in cmd:
        print("Sonu: Turning left.")
        left()
        return

    if "right" in cmd:
        print("Sonu: Turning right.")
        right()
        return

    # CHAT
    print("Sonu: Let me think...")
    reply = chat_with_llm(cmd)
    print("Sonu:", reply)

# ------------------------------
def main():
    global CONTINUOUS_MODE

    print("Sonu is online. Say Hey Sonu.")
    stream.start()

    while True:
        print("[MODE] Sleeping...")
        text = listen()

        if any(w in text for w in WAKE_PHRASE):
            print("Sonu: I'm listening.")
        else:
            continue

        while True:
            text = listen()

            if text.strip() == "":
                continue

            if any(w in text for w in WAKE_PHRASE):
                print("Sonu: Yes?")
                continue

            if "sleep" in text:
                print("Sonu: Going to sleep.")
                CONTINUOUS_MODE = False
                stop()
                break

            handle_command(text)

# ------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop()
        print("Sonu shutting down...")
