import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import config, BASE_DIR
from app.obs.connection import obs_connection
from app.audio.level_monitor import level_monitor
from app.audio.auto_switcher import auto_switcher
from app.voice.recognizer import vosk_recognizer
from app.voice.command_parser import command_parser
from app.voice.command_registry import command_registry
from app.api import scenes, switching, assets, voice, status, websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _on_audio_levels(levels_db: list[float]):
    """Called from audio thread with per-channel levels."""
    auto_switcher.process_levels(levels_db)

    # Feed producer channel to voice recognizer
    # Note: we only get dB levels here, not raw audio.
    # Raw audio feeding happens in the level_monitor callback integration below.


def _on_voice_text(text: str):
    """Called when Vosk recognizes speech."""
    result = command_parser.parse(text)
    if result:
        command_registry.execute(result)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  UNCAPPED Production Control")
    logger.info("  Starting up...")
    logger.info("=" * 60)

    # Connect to OBS
    if obs_connection.connect():
        version = obs_connection.get_version()
        logger.info("OBS version: %s", version)
        scenes_list = []
        try:
            from app.obs.scene_manager import scene_manager
            scenes_list = scene_manager.get_scene_list()
        except Exception:
            pass
        logger.info("Available scenes: %s", scenes_list)
    else:
        logger.warning("Could not connect to OBS. Will retry in background.")

    # Start OBS reconnect loop
    reconnect_task = asyncio.create_task(obs_connection.start_reconnect_loop())

    # Start audio monitoring
    level_monitor.on_levels(_on_audio_levels)
    if level_monitor.start():
        logger.info("Audio monitoring active")
    else:
        logger.warning("Audio monitoring not available (Scarlett not found)")

    # Set up voice recognition
    vosk_recognizer.on_text(_on_voice_text)

    logger.info("=" * 60)
    logger.info("  Dashboard: http://localhost:%d", config.server.port)
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down...")
    vosk_recognizer.stop()
    level_monitor.stop()
    obs_connection.disconnect()
    reconnect_task.cancel()


app = FastAPI(title="Uncapped Production Control", lifespan=lifespan)

# Mount API routers
app.include_router(scenes.router)
app.include_router(switching.router)
app.include_router(assets.router)
app.include_router(voice.router)
app.include_router(status.router)
app.include_router(websocket.router)

# Serve frontend
frontend_dir = BASE_DIR / "frontend"
app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")


@app.get("/")
async def root():
    return FileResponse(str(frontend_dir / "index.html"))
