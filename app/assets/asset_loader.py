import logging
from pathlib import Path

from app.obs.source_manager import source_manager
from app.obs.scene_manager import scene_manager

logger = logging.getLogger(__name__)


INPUT_KINDS = {
    ".png": "image_source",
    ".jpg": "image_source",
    ".jpeg": "image_source",
    ".bmp": "image_source",
    ".gif": "image_source",
    ".webp": "image_source",
    ".mp4": "ffmpeg_source",
    ".mkv": "ffmpeg_source",
    ".mov": "ffmpeg_source",
    ".avi": "ffmpeg_source",
    ".webm": "ffmpeg_source",
    ".flv": "ffmpeg_source",
    ".mp3": "ffmpeg_source",
    ".wav": "ffmpeg_source",
    ".ogg": "ffmpeg_source",
    ".flac": "ffmpeg_source",
    ".aac": "ffmpeg_source",
    ".m4a": "ffmpeg_source",
}


class AssetLoader:
    def load_to_scene(self, file_path: str, scene_name: str = None,
                      input_name: str = None) -> dict:
        """Load a media file into OBS as a source in the specified scene."""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        ext = path.suffix.lower()
        input_kind = INPUT_KINDS.get(ext)
        if not input_kind:
            return {"success": False, "error": f"Unsupported file type: {ext}"}

        if scene_name is None:
            scene_name = scene_manager.get_current_scene()
            if not scene_name:
                return {"success": False, "error": "No active scene"}

        if input_name is None:
            input_name = f"Asset: {path.stem}"

        # Remove existing source with same name
        try:
            source_manager.remove_input(input_name)
        except Exception:
            pass

        # Build settings based on input kind
        if input_kind == "image_source":
            settings = {"file": str(path.resolve())}
        else:
            settings = {
                "local_file": str(path.resolve()),
                "is_local_file": True,
                "looping": ext in {".mp3", ".wav", ".ogg", ".flac"},
            }

        item_id = source_manager.create_input(
            scene_name, input_name, input_kind, settings
        )
        if item_id is not None:
            logger.info("Loaded asset '%s' into scene '%s'", path.name, scene_name)
            return {"success": True, "input_name": input_name, "scene": scene_name, "item_id": item_id}
        else:
            return {"success": False, "error": "Failed to create input in OBS"}

    def remove_from_scene(self, input_name: str) -> dict:
        success = source_manager.remove_input(input_name)
        return {"success": success}


asset_loader = AssetLoader()
