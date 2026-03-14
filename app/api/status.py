from fastapi import APIRouter

from app.obs.connection import obs_connection
from app.audio.level_monitor import level_monitor
from app.audio.auto_switcher import auto_switcher
from app.voice.recognizer import vosk_recognizer
from app.obs.scene_manager import scene_manager

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("")
def get_status():
    obs_version = obs_connection.get_version() if obs_connection.connected else None
    return {
        "obs": {
            "connected": obs_connection.connected,
            "version": obs_version,
            "current_scene": scene_manager.get_current_scene() if obs_connection.connected else None,
        },
        "audio": {
            "running": level_monitor.running,
            "levels_db": level_monitor.levels_db if level_monitor.running else None,
        },
        "auto_switch": auto_switcher.get_state(),
        "voice": {
            "running": vosk_recognizer.running,
        },
    }
