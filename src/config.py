from pathlib import Path

# Root of the project (…/sonu-robot)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -------- Audio / STT --------
VOICE_DIR = PROJECT_ROOT / "voice"
MODEL_PATH = VOICE_DIR / "model"          # folder containing Vosk model files
SOUNDS_DIR = VOICE_DIR / "sounds"
IDLE_SOUND = SOUNDS_DIR / "purr.wav"      # cat-like breathing sound

# Change this if your mic index changes
MIC_DEVICE_INDEX = 1

# -------- LLM / Ollama --------
# Set this to your laptop's LAN IP (you already used 192.168.1.34)
LLM_HOST = "192.168.1.34"
LLM_PORT = 11434
LLM_MODEL = "phi3:mini"

# -------- Movement tuning --------
STEP_FORWARD_SEC = 1.5
STEP_TURN_SEC = 0.8
LONG_MOVE_SEC = 999.0   # for "continue moving forward" etc.
