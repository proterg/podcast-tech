import logging
from typing import Optional

from app.obs.connection import obs_connection

logger = logging.getLogger(__name__)


class SceneManager:
    def get_current_scene(self) -> Optional[str]:
        client = obs_connection.client
        if not client:
            return None
        try:
            resp = client.get_current_program_scene()
            return resp.scene_name
        except Exception as e:
            logger.error("Failed to get current scene: %s", e)
            return None

    def get_scene_list(self) -> list[str]:
        client = obs_connection.client
        if not client:
            return []
        try:
            resp = client.get_scene_list()
            return [s["sceneName"] for s in resp.scenes]
        except Exception as e:
            logger.error("Failed to get scene list: %s", e)
            return []

    def switch_scene(self, scene_name: str) -> bool:
        client = obs_connection.client
        if not client:
            logger.error("OBS not connected")
            return False
        try:
            client.set_current_program_scene(scene_name)
            logger.info("Switched to scene: %s", scene_name)
            return True
        except Exception as e:
            logger.error("Failed to switch to scene '%s': %s", scene_name, e)
            return False

    def get_preview_scene(self) -> Optional[str]:
        client = obs_connection.client
        if not client:
            return None
        try:
            resp = client.get_current_preview_scene()
            return resp.scene_name
        except Exception:
            return None

    def set_preview_scene(self, scene_name: str) -> bool:
        client = obs_connection.client
        if not client:
            return False
        try:
            client.set_current_preview_scene(scene_name)
            return True
        except Exception as e:
            logger.error("Failed to set preview scene: %s", e)
            return False


scene_manager = SceneManager()
