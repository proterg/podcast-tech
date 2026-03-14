# Uncapped Production Control

Web-based production control panel for the Uncapped podcast. Sits between the operator and OBS so OBS never needs to be touched directly during a show.

## Architecture

**Python (FastAPI) backend** on `localhost:8080` + **vanilla JS frontend** (no build step).

```
Browser (operator)  <--WebSocket/REST-->  FastAPI backend  <--obsws-python-->  OBS
                                              |
                                     sounddevice (WASAPI shared mode)
                                              |
                                       Scarlett 18i20 (7 mic channels)
                                              |
                                       Vosk (offline speech recognition)
```

## Quick Start

```bash
python run.py
# Open http://localhost:8080
```

### Prerequisites
- Python 3.12 (installed via winget)
- OBS 32+ with WebSocket enabled (Tools > WebSocket Server Settings)
- Focusrite Scarlett 18i20 connected via USB
- Dependencies: `pip install -r requirements.txt`

## Project Structure

- `app/obs/` -- OBS WebSocket connection, scene switching, source management, scene builder
- `app/audio/` -- WASAPI audio capture, per-channel RMS levels, auto-switch algorithm
- `app/voice/` -- Vosk speech recognition, fuzzy command matching, command routing
- `app/assets/` -- File browser for media assets, OBS source loader
- `app/api/` -- FastAPI routes (scenes, switching, assets, voice, status, WebSocket)
- `frontend/` -- Single-page dashboard (vanilla HTML/CSS/JS, no framework, no build step)
- `config/` -- JSON configs for mic mapping, voice commands, scene templates
- `assets/` -- Operator drops media files here (graphics, lower-thirds, video, audio)
- `models/` -- Vosk speech model directory

## Key Technical Details

### Audio
- WASAPI **shared mode** so both this app and OBS can read from the Scarlett simultaneously
- 48kHz, 1024-frame blocks (~21ms latency), 8 channels
- Channel mapping in `config/mic_mapping.json`

### Auto-Switch Algorithm
- Threshold: -40 dB, Debounce: 800ms, Cooldown: 2000ms, Hysteresis: 3 dB
- Host wins ties, then co-host, then contributors
- 3+ speakers for 1s triggers Gallery view
- Channels 2+3 and 4+5 share cameras (2-shot grouping)

### OBS Integration
- Uses `obsws-python` (WebSocket v5 protocol)
- Existing scenes: Camera 1-4 (from OBS scene collection)
- Source names: Cam 1 (Cam Link 4K USB), Cam 2-4 (DeckLink Duo SDI)
- App creates additional scenes dynamically (Gallery, Split, PiP)

### Voice Commands
- Vosk offline model on producer mic channel (ch 6)
- Fuzzy matching with thefuzz (threshold 0.70)
- 2-second cooldown between commands

## Development Notes

- Frontend uses no framework -- plain JS components in `frontend/js/components/`
- WebSocket broadcasts audio levels at 20fps + scene state
- REST API for all commands
- Keyboard shortcuts: 1-4 cameras, G gallery, A auto-switch, V voice
- All config is in JSON files under `config/` -- no env vars needed for basic setup
- OBS password can be set in `app/config.py` (AppConfig.obs.password) if configured
