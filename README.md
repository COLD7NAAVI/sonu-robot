# Sonu Robot (Raspberry Pi 5 + L298N + Ollama)

Voice-controlled cat-like robot using:
- Raspberry Pi 5
- Vosk (offline STT)
- L298N motor driver
- Ollama LLM running on a laptop on the same LAN
- Simple espeak TTS

## Setup on Raspberry Pi

```bash
sudo apt update
sudo apt install python3-pip python3-libgpiod sox espeak git

# Clone repo
cd ~
git clone https://github.com/YOUR_USERNAME/sonu-robot.git
cd sonu-robot

# Python deps
python3 -m pip install -r requirements.txt
