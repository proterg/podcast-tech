from fastapi import APIRouter
from pydantic import BaseModel

from app.voice.recognizer import vosk_recognizer
from app.voice.command_registry import command_registry

router = APIRouter(prefix="/api/voice", tags=["voice"])


class VoiceToggle(BaseModel):
    enabled: bool


@router.get("")
def get_status():
    last = command_registry.last_command
    return {
        "running": vosk_recognizer.running,
        "last_command": last,
    }


@router.post("/toggle")
def toggle(req: VoiceToggle):
    if req.enabled:
        success = vosk_recognizer.start()
    else:
        vosk_recognizer.stop()
        success = True
    return {"success": success, "running": vosk_recognizer.running}
