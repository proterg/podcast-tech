import json
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = BASE_DIR / "models"


class OBSConfig(BaseModel):
    host: str = "localhost"
    port: int = 4455
    password: str = ""


class AudioConfig(BaseModel):
    device_name: str = "Focusrite USB Audio"
    sample_rate: int = 48000
    block_size: int = 1024
    num_channels: int = 8


class AutoSwitchConfig(BaseModel):
    enabled: bool = False
    threshold_db: float = -40.0
    debounce_ms: int = 800
    cooldown_ms: int = 2000
    hysteresis_db: float = 3.0
    gallery_trigger_channels: int = 3
    gallery_trigger_ms: int = 1000


class VoiceConfig(BaseModel):
    enabled: bool = False
    model_path: str = str(MODELS_DIR / "vosk-model-small-en-us-0.15")
    match_threshold: float = 0.70
    cooldown_seconds: float = 2.0
    producer_channel: int = 6


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class AppConfig(BaseSettings):
    obs: OBSConfig = OBSConfig()
    audio: AudioConfig = AudioConfig()
    auto_switch: AutoSwitchConfig = AutoSwitchConfig()
    voice: VoiceConfig = VoiceConfig()
    server: ServerConfig = ServerConfig()


def load_mic_mapping() -> dict:
    path = CONFIG_DIR / "mic_mapping.json"
    with open(path) as f:
        return json.load(f)


def load_voice_commands() -> dict:
    path = CONFIG_DIR / "voice_commands.json"
    with open(path) as f:
        return json.load(f)


def load_scene_templates() -> dict:
    path = CONFIG_DIR / "scene_templates.json"
    with open(path) as f:
        return json.load(f)


config = AppConfig()
