# src/config.py
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
VOICE_DIR = BASE_DIR / "voice"
MODEL_PATH = VOICE_DIR / "model"

# idle breathing / purring sound
IDLE_SOUND = VOICE_DIR / "sounds" / "purr.wav"

# ---------- Audio / mic ----------
# Use the index that worked for you before (USB PnP Sound Device).
MIC_DEVICE_INDEX = 1          # change if your mic index is different
SAMPLE_RATE = 44100           # will be checked at runtime

# ---------- Wake / sleep words ----------
WAKE_PHRASES = [
    "hey sonu",
    "hey sono",
    "hey so new",
    "hey son"
]

SLEEP_PHRASES = [
    "you can sleep now",
    "go to sleep",
    "sleep now",
    "take rest",
    "sonu sleep",
]

# Movement command words
COMMAND_WORDS = [
    "forward",
    "backward",
    "back",
    "left",
    "right",
    "stop",
    "continue moving forward",
    "continue forward",
    "continue moving back",
    "continue backward",
    "continue left",
    "continue right",
]

# ---------- LLM server (your laptop / Ollama) ----------
LLM_HOST = "192.168.1.8"     # your laptop’s IP on Wi-Fi
LLM_PORT = 11434
LLM_MODEL = "phi3:mini"
# ===== Movement Durations (seconds) =====

STEP_FORWARD_SEC = 1.0
STEP_BACKWARD_SEC = 1.0
STEP_LEFT_SEC = 0.7
STEP_RIGHT_SEC = 0.7
