# Jarvis

Personal AI assistant. Starts as a text-based chat brain, grows into
voice + smart home control over time.

## Setup (any machine)

```bash
git clone <your-repo-url>
cd jarvis
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your real ANTHROPIC_API_KEY
python jarvis.py
```

## Roadmap
- [x] Text chat brain (this)
- [ ] Give it tools (smart home control via Home Assistant API)
- [ ] Add voice input (Whisper)
- [ ] Add voice output (TTS)
- [ ] Wake word ("Hey Jarvis")
- [ ] Deploy as always-on service on Mac mini
