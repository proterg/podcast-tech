import asyncio
import json
import logging
import time
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.audio.level_monitor import level_monitor
from app.audio.auto_switcher import auto_switcher
from app.obs.scene_manager import scene_manager
from app.obs.connection import obs_connection
from app.config import load_mic_mapping
from app.voice.command_registry import command_registry

logger = logging.getLogger(__name__)

router = APIRouter()

_active_connections: Set[WebSocket] = set()
_mic_mapping = None


def _get_mic_mapping():
    global _mic_mapping
    if _mic_mapping is None:
        _mic_mapping = load_mic_mapping()
    return _mic_mapping


async def broadcast(data: dict):
    """Send data to all connected WebSocket clients."""
    if not _active_connections:
        return
    message = json.dumps(data)
    disconnected = set()
    for ws in _active_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    _active_connections.difference_update(disconnected)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _active_connections.add(ws)
    logger.info("WebSocket client connected (%d total)", len(_active_connections))

    try:
        # Send initial state
        mapping = _get_mic_mapping()
        await ws.send_text(json.dumps({
            "type": "init",
            "mic_mapping": mapping["channels"],
            "obs_connected": obs_connection.connected,
            "current_scene": scene_manager.get_current_scene() if obs_connection.connected else None,
            "auto_switch": auto_switcher.get_state(),
        }))

        # Broadcast loop: send audio levels at ~20fps
        while True:
            if level_monitor.running:
                levels = level_monitor.levels_db
                mapping = _get_mic_mapping()
                await ws.send_text(json.dumps({
                    "type": "levels",
                    "levels_db": levels,
                    "timestamp": time.time(),
                }))

            # Check for scene changes and voice commands
            current = scene_manager.get_current_scene() if obs_connection.connected else None
            last_cmd = command_registry.last_command
            await ws.send_text(json.dumps({
                "type": "state",
                "current_scene": current,
                "auto_switch": auto_switcher.get_state(),
                "voice_last_command": last_cmd,
                "obs_connected": obs_connection.connected,
            }))

            await asyncio.sleep(0.05)  # 20fps

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("WebSocket error: %s", e)
    finally:
        _active_connections.discard(ws)
        logger.info("WebSocket client disconnected (%d remaining)", len(_active_connections))
