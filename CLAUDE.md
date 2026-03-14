# Uncapped Production Control

Web-based production control panel for the Uncapped podcast. Sits between the operator and OBS so OBS never needs to be touched directly during a show.

## Architecture

**Python (FastAPI) backend** on `localhost:8080` + **vanilla JS frontend** (no build step).

```
Browser (operator)  <--WebSocket/REST-->  FastAPI backend  <--obsws-python-->  OBS
                                                                               |
                                                                        ASIO (exclusive)
                                                                               |
                                                                     Scarlett 18i20 (7 mics)
```

Audio flows: Scarlett → ASIO → OBS (owns all audio). The control app manages OBS over WebSocket -- it does NOT access the Scarlett directly.

## Quick Start

```bash
python run.py
# Open http://localhost:8080
```

### Prerequisites
- Python 3.12 (installed via winget)
- OBS 32+ with WebSocket enabled (Tools > WebSocket Server Settings)
- OBS ASIO plugin (obs-asio v3.2.1f) for multi-channel Focusrite input
- Focusrite Scarlett 18i20 connected via USB
- Focusrite Control 3.27+ for hardware routing/gain
- Dependencies: `pip install -r requirements.txt`

## Project Structure

- `app/obs/` -- OBS WebSocket connection, scene switching, source management, scene builder
- `app/audio/` -- Auto-switch algorithm, audio level processing (via OBS WebSocket)
- `app/voice/` -- Vosk speech recognition, fuzzy command matching, command routing
- `app/callin/` -- VDO.Ninja call-in management (invite links, OBS browser sources)
- `app/assets/` -- File browser for media assets, OBS source loader
- `app/api/` -- FastAPI routes (scenes, switching, assets, voice, status, WebSocket, **runofshow**)
- `frontend/` -- Single-page dashboard (vanilla HTML/CSS/JS, no framework, no build step)
- `config/` -- JSON configs for mic mapping, voice commands, scene templates, **run of show**
- `assets/` -- Media files (graphics, lower-thirds, video, audio). Pre-production uploads land here.
- `models/` -- Vosk speech model directory

## Dashboard Modes

The dashboard has two global views toggled via the header nav:

### Pre-Production
- **Run of Show editor** -- segments: Intro, A Block, B Block, ... Outro
- Each segment is a card with topic/description, notes, and an asset drop zone
- Segments are drag-and-drop reorderable (grab the ☰ handle)
- New segments insert before Outro and auto-assign the next letter
- Each segment has a distinct color (left border) for visual distinction
- Assets: drag files from desktop onto a block, or click the drop zone to browse
- Uploaded files are saved to `assets/` and linked to the segment
- Data persists in `config/runofshow.json`
- Max-width 800px centered layout for readability

### Live
- Scene switching (Camera 1-4, Gallery, custom layouts)
- Real-time audio meters (7 channels)
- Auto-switch controls with threshold/debounce/cooldown tuning
- Bottom tabs: Assets, Lower Thirds, Voice, Call-In, Scene Builder
- Keyboard shortcuts: 1-4 cameras, G gallery, A auto-switch, V voice

## Key Technical Details

### Audio
- OBS owns all audio via ASIO (Focusrite USB ASIO driver, exclusive mode)
- 7 SM7B mics on Scarlett 18i20 inputs 1-7, each as an ASIO Input Capture source in OBS
- Control app reads audio levels and controls volume/mute via OBS WebSocket
- Channel mapping in `config/mic_mapping.json`

### Auto-Switch Algorithm
- Threshold: -40 dB, Debounce: 800ms, Cooldown: 2000ms, Hysteresis: 3 dB
- Host wins ties, then co-host, then contributors
- 3+ speakers for 1s triggers Gallery view
- Channels 2+3 and 4+5 share cameras (2-shot grouping)

### OBS Integration
- Uses `obsws-python` (WebSocket v5 protocol)
- OBS password configured in `app/config.py` (AppConfig.obs.password)
- Existing scenes: Camera 1-4 (from OBS scene collection)
- Source names: Cam 1 (Cam Link 4K USB), Cam 2-4 (DeckLink Duo SDI)
- App creates additional scenes dynamically (Gallery, Split, PiP)

### Call-In (Remote Guests)
- Up to 2 simultaneous call-in slots via VDO.Ninja (peer-to-peer WebRTC)
- No server or account needed -- guests open a browser link to send webcam/mic
- Each slot creates an OBS Browser Source (`Call-In 1`, `Call-In 2`)
- Scene templates include split/gallery layouts with call-in sources
- Use cases: remote guests, on-field reporters

### Voice Commands
- Vosk offline model on producer mic channel (ch 6)
- Fuzzy matching with thefuzz (threshold 0.70)
- 2-second cooldown between commands

### Run of Show (Pre-Production)
- API: `GET/POST /api/runofshow`, `POST /api/runofshow/segment`, `DELETE /api/runofshow/segment/{id}`, `POST /api/runofshow/upload/{segment_id}`
- File uploads use `python-multipart` (FastAPI `UploadFile`)
- Segment model: id, label, title, notes, assets[]
- Pre-Production drives Live -- not the other way around

## Development Notes

- Frontend uses no framework -- plain JS components in `frontend/js/components/`
- WebSocket broadcasts audio levels at 20fps + scene state
- REST API for all commands
- All config is in JSON files under `config/` -- no env vars needed for basic setup
- To restart the server: kill the python process on port 8080, then `python run.py`
