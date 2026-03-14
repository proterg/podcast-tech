import logging

from app.obs.scene_manager import scene_manager
from app.obs.scene_builder import scene_builder
from app.audio.auto_switcher import auto_switcher

logger = logging.getLogger(__name__)


class CommandRegistry:
    """Routes parsed voice commands to the appropriate actions."""

    def __init__(self):
        self._last_command = None

    def execute(self, command: dict) -> dict:
        action = command["action"]
        params = command.get("params", {})
        self._last_command = command

        handler = getattr(self, f"_handle_{action}", None)
        if handler:
            return handler(params)
        else:
            logger.warning("Unknown command action: %s", action)
            return {"success": False, "error": f"Unknown action: {action}"}

    def _handle_switch_scene(self, params: dict) -> dict:
        scene = params.get("scene")
        if not scene:
            return {"success": False, "error": "No scene specified"}
        success = scene_manager.switch_scene(scene)
        return {"success": success, "scene": scene}

    def _handle_play_asset(self, params: dict) -> dict:
        # TODO: Integrate with asset loader
        asset_type = params.get("type", "")
        logger.info("Play asset requested: %s", asset_type)
        return {"success": True, "asset_type": asset_type, "note": "Asset playback not yet implemented"}

    def _handle_lower_third(self, params: dict) -> dict:
        name = params.get("name", "")
        title = params.get("title", "")
        if name:
            success = scene_builder.build_lower_third_scene(name, title)
        else:
            success = scene_builder.hide_lower_third()
        return {"success": success}

    def _handle_auto_switch(self, params: dict) -> dict:
        enabled = params.get("enabled", False)
        auto_switcher.enabled = enabled
        return {"success": True, "enabled": enabled}

    @property
    def last_command(self) -> dict:
        return self._last_command


command_registry = CommandRegistry()
