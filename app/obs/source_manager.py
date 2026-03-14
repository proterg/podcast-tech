import logging
from typing import Optional

from app.obs.connection import obs_connection

logger = logging.getLogger(__name__)


class SourceManager:
    def get_scene_items(self, scene_name: str) -> list[dict]:
        client = obs_connection.client
        if not client:
            return []
        try:
            resp = client.get_scene_item_list(scene_name)
            return resp.scene_items
        except Exception as e:
            logger.error("Failed to get scene items for '%s': %s", scene_name, e)
            return []

    def create_input(self, scene_name: str, input_name: str, input_kind: str,
                     input_settings: dict, enabled: bool = True) -> Optional[int]:
        client = obs_connection.client
        if not client:
            return None
        try:
            resp = client.create_input(
                scene_name, input_name, input_kind, input_settings, enabled
            )
            logger.info("Created input '%s' in scene '%s'", input_name, scene_name)
            return resp.scene_item_id
        except Exception as e:
            logger.error("Failed to create input '%s': %s", input_name, e)
            return None

    def remove_input(self, input_name: str) -> bool:
        client = obs_connection.client
        if not client:
            return False
        try:
            client.remove_input(input_name)
            logger.info("Removed input '%s'", input_name)
            return True
        except Exception as e:
            logger.error("Failed to remove input '%s': %s", input_name, e)
            return False

    def set_item_transform(self, scene_name: str, item_id: int,
                           x: float, y: float, width: float, height: float) -> bool:
        client = obs_connection.client
        if not client:
            return False
        try:
            transform = {
                "positionX": x,
                "positionY": y,
                "boundsType": "OBS_BOUNDS_STRETCH",
                "boundsWidth": width,
                "boundsHeight": height,
                "boundsAlignment": 0,
            }
            client.set_scene_item_transform(scene_name, item_id, transform)
            return True
        except Exception as e:
            logger.error("Failed to set transform for item %d: %s", item_id, e)
            return False

    def set_item_enabled(self, scene_name: str, item_id: int, enabled: bool) -> bool:
        client = obs_connection.client
        if not client:
            return False
        try:
            client.set_scene_item_enabled(scene_name, item_id, enabled)
            return True
        except Exception as e:
            logger.error("Failed to set enabled for item %d: %s", item_id, e)
            return False

    def get_item_id(self, scene_name: str, source_name: str) -> Optional[int]:
        client = obs_connection.client
        if not client:
            return None
        try:
            resp = client.get_scene_item_id(scene_name, source_name)
            return resp.scene_item_id
        except Exception:
            return None

    def add_existing_source(self, scene_name: str, source_name: str) -> Optional[int]:
        """Add an existing source to a scene (creates a scene item reference)."""
        client = obs_connection.client
        if not client:
            return None
        try:
            resp = client.create_scene_item(scene_name, source_name)
            return resp.scene_item_id
        except Exception as e:
            logger.error("Failed to add source '%s' to scene '%s': %s", source_name, scene_name, e)
            return None


source_manager = SourceManager()
