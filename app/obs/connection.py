import asyncio
import logging
from typing import Optional

import obsws_python as obs

from app.config import config

logger = logging.getLogger(__name__)


class OBSConnection:
    """Manages the OBS WebSocket connection with auto-reconnect."""

    def __init__(self):
        self._client: Optional[obs.ReqClient] = None
        self._event_client: Optional[obs.EventClient] = None
        self._connected = False
        self._on_scene_change_callbacks = []
        self._reconnect_task: Optional[asyncio.Task] = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def client(self) -> Optional[obs.ReqClient]:
        return self._client

    def connect(self) -> bool:
        try:
            self._client = obs.ReqClient(
                host=config.obs.host,
                port=config.obs.port,
                password=config.obs.password,
                timeout=5,
            )
            self._connected = True
            logger.info("Connected to OBS WebSocket at %s:%d", config.obs.host, config.obs.port)

            # Set up event client for scene change notifications
            try:
                self._event_client = obs.EventClient(
                    host=config.obs.host,
                    port=config.obs.port,
                    password=config.obs.password,
                )
                self._event_client.callback.register(self._on_current_program_scene_changed)
                logger.info("OBS event client connected")
            except Exception as e:
                logger.warning("Could not connect event client: %s", e)

            return True
        except Exception as e:
            self._connected = False
            logger.error("Failed to connect to OBS: %s", e)
            return False

    def disconnect(self):
        self._connected = False
        if self._event_client:
            try:
                self._event_client.disconnect()
            except Exception:
                pass
            self._event_client = None
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None
        logger.info("Disconnected from OBS")

    def on_scene_change(self, callback):
        self._on_scene_change_callbacks.append(callback)

    def _on_current_program_scene_changed(self, data):
        scene_name = data.scene_name
        for cb in self._on_scene_change_callbacks:
            try:
                cb(scene_name)
            except Exception as e:
                logger.error("Scene change callback error: %s", e)

    async def start_reconnect_loop(self):
        """Background task to reconnect if connection drops."""
        while True:
            if not self._connected:
                logger.info("Attempting OBS reconnect...")
                self.connect()
            await asyncio.sleep(5)

    def get_version(self) -> Optional[str]:
        if not self._client:
            return None
        try:
            resp = self._client.get_version()
            return resp.obs_version
        except Exception:
            self._connected = False
            return None


obs_connection = OBSConnection()
