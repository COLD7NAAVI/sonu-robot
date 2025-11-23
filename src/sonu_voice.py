#!/usr/bin/env python3
import json
import random
import threading
import time
import subprocess
import sys

import sounddevice as sd
from vosk import Model, KaldiRecognizer

import config
from motor_drive import forward, backward, left, right, stop_all
from llm_brain import ask_brain


# ---------------------------------------------------------
#  Idle sound (cat-like breathing)
# ---------------------------------------------------------
IDLE_SOUND_PATH = str(config.IDLE_SOUND)
idle_running = False
idle_thread = None


def play_idle_sound():
    global idle_running
    while idle_running:
        subprocess.call(["aplay", "-q", IDLE_SOUND_PATH])
        time.sleep(0.1)


def start_idle_sound():
    global idle_running, idle_thread
    if idle_running:
        return
    idle_running = True
    idle_thread = threading.Thread(target=play_idle_sound, daemon=True)
    idle_thread.start()


def stop_idle_sound():
    global idle_running
    idle_running = False


# ---------------------------------------------------------
#  Config / phrases
# ---------------------------------------------------------
MODEL_PATH = str(config.MODEL_PATH)

WAKE_PHRASES = [
    "hey sonu",
    "hey son",
    "hey soonu",
    "hey sono",
]

SLEEP_PHRASES = [
    "you can sleep now",
    "sleep now",
    "go to sleep",
    "go sleep",
    "take rest",
    "sonu sleep",
]

MOVE_WORDS = ["forward", "backward", "back", "left", "right", "stop"]
CONTINUE_WORDS = [
    "continue moving forward",
    "continue forward",
    "continue moving back",
    "continue backward",
    "continue left",
    "continue right",
]

RESP_WAKE = [
    "Standing by.",
    "Yes, I'm here.",
    "Ready.",
    "Listening.",
]

RESP_FORWARD = ["Moving forward.", "Advancing."]
RESP_BACKWARD = ["Moving back.", "Retreating."]
RESP_LEFT = ["Turning left."]
RESP_RIGHT = ["Turning right."]
RESP_STOP = ["Stopping.", "Hold position."]
RESP_NO_COMMAND = ["I didn't understand.", "Please repeat."]
RESP_SLEEP = ["Going to sleep.", "Okay, sleeping."]


# ---------------------------------------------------------
#  TTS helper
# ---------------------------------------------------------
def speak(text: str):
    text = text.strip()
    if not text:
        return
    print(f"Sonu says: {text}")
    subprocess.run(["espeak", "-s", "160", text])


# ---------------------------------------------------------
#  Audio + Vosk setup
# ---------------------------------------------------------
def setup_audio():
    devices = sd.query_devices()
    print("\nAvailable devices:")
    for i, dev in enumerate(devices):
        print(f"{i}: {dev['name']}, in={dev['max_input_channels']}, out={dev['max_output_channels']}")

    dev_info = sd.query_devices(config.MIC_DEVICE_INDEX, "input")
    sample_rate = int(dev_info["default_samplerate"])

    print(f"\nChosen mic device index: {config.MIC_DEVICE_INDEX}")
    print(f"Using sample rate: {sample_rate} Hz")

    return sample_rate


SAMPLE_RATE = setup_audio()

print("\nLoading Vosk model...")
model = Model(MODEL_PATH)
print("Vosk model loaded.")


def build_grammar(words):
    return json.dumps(words)


WAKE_GRAMMAR = build_grammar(WAKE_PHRASES)


def is_wake(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in WAKE_PHRASES)


def is_sleep(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in SLEEP_PHRASES)


def classify_intent(text: str) -> str:
    t = text.lower()
    if is_sleep(t):
        return "sleep"
    if any(w in t for w in MOVE_WORDS) or any(w in t for w in CONTINUE_WORDS):
        return "move"
    return "chat"


# ---------------------------------------------------------
#  STT with Vosk only
# ---------------------------------------------------------
def listen_once(timeout: float, mode: str) -> str:
    if mode == "wake":
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, WAKE_GRAMMAR)
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    result_text = ""

    def callback(indata, frames, time_info, status):
        nonlocal result_text
        if status:
            print("SD status:", status)

        if not indata:
            return

        try:
            data_bytes = bytes(indata)
            if recognizer.AcceptWaveform(data_bytes):
                res = json.loads(recognizer.Result())
                text = res.get("text", "")
                if text:
                    print("[HEARD RAW]:", text)
                    result_text = text.lower()
        except Exception as e:
            print("Vosk callback error:", e)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        dtype="int16",
        channels=1,
        device=config.MIC_DEVICE_INDEX,
        callback=callback,
    ):
        start = time.time()
        while time.time() - start < timeout and not result_text:
            time.sleep(0.05)

    if not result_text:
        try:
            res = json.loads(recognizer.FinalResult())
            text = res.get("text", "")
            if text:
                print("[FINAL RAW]:", text)
                result_text = text.lower()
        except Exception:
            pass

    return result_text.strip()


# ---------------------------------------------------------
#  Movement handling
# ---------------------------------------------------------
continuous_state = None  # 'forward', 'backward', 'left', 'right' or None


def handle_move_command(text: str):
    global continuous_state

    t = text.lower()
    print(f"[COMMAND] Heard: {t!r}")
    stop_all()

    # Continuous moves
    if "continue moving forward" in t or "continue forward" in t:
        continuous_state = "forward"
        speak(random.choice(RESP_FORWARD))
        forward(config.LONG_MOVE_SEC)
        return
    if "continue moving back" in t or "continue backward" in t:
        continuous_state = "backward"
        speak(random.choice(RESP_BACKWARD))
        backward(config.LONG_MOVE_SEC)
        return
    if "continue left" in t:
        continuous_state = "left"
        speak(random.choice(RESP_LEFT))
        left(config.LONG_MOVE_SEC)
        return
    if "continue right" in t:
        continuous_state = "right"
        speak(random.choice(RESP_RIGHT))
        right(config.LONG_MOVE_SEC)
        return

    # Single steps
    continuous_state = None

    if "forward" in t:
        speak(random.choice(RESP_FORWARD))
        forward(config.STEP_FORWARD_SEC)
    elif "backward" in t or "back" in t:
        speak(random.choice(RESP_BACKWARD))
        backward(config.STEP_FORWARD_SEC)
    elif "left" in t:
        speak(random.choice(RESP_LEFT))
        left(config.STEP_TURN_SEC)
    elif "right" in t:
        speak(random.choice(RESP_RIGHT))
        right(config.STEP_TURN_SEC)
    elif "stop" in t:
        speak(random.choice(RESP_STOP))
        stop_all()
        continuous_state = None
    else:
        speak(random.choice(RESP_NO_COMMAND))


# ---------------------------------------------------------
#  Chat handling via LLM
# ---------------------------------------------------------
def handle_chat(text: str):
    print(f"[CHAT] Sending to brain: {text!r}")
    try:
        llm_prompt = (
            "You are Sonu, a small cute cat-like exploration robot. "
            "Answer briefly in one or two short sentences. "
            "User said: " + text
        )
        reply = ask_brain(llm_prompt)
    except Exception as e:
        print("[LLM ERROR]", e)
        speak("I had a problem thinking.")
        return

    speak(reply)


# ---------------------------------------------------------
#  Main loop
# ---------------------------------------------------------
def main():
    awake = False
    start_idle_sound()
    speak("Voice control online. Say Hey Sonu to wake me.")

    while True:
        if not awake:
            print("\n[MODE] Sleeping...")
            print("[LISTEN] Waiting for wake phrase 'Hey Sonu'...")
            text = listen_once(timeout=6.0, mode="wake")
            if not text:
                continue

            print(f"[HEARD]: {text}")
            if is_wake(text):
                awake = True
                speak(random.choice(RESP_WAKE))
            continue

        print("\n[MODE] Awake - waiting for commands or questions")
        text = listen_once(timeout=7.0, mode="command")
        if not text:
            continue

        print(f"[HEARD]: {text}")

        if is_wake(text):
            speak("Yes?")
            continue

        intent = classify_intent(text)
        print(f"[INTENT]: {intent}")

        if intent == "sleep":
            speak(random.choice(RESP_SLEEP))
            stop_all()
            global continuous_state
            continuous_state = None
            awake = False
            continue

        if intent == "move":
            handle_move_command(text)
        else:
            handle_chat(text)

        time.sleep(0.2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. Stopping motors.")
        stop_all()
        stop_idle_sound()
        sys.exit(0)
