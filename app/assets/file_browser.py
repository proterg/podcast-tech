import logging
from pathlib import Path

from app.config import ASSETS_DIR

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    "graphics": {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".svg"},
    "lower-thirds": {".png", ".jpg", ".jpeg", ".html"},
    "video": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"},
    "audio": {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"},
}

ALL_SUPPORTED = set()
for exts in SUPPORTED_EXTENSIONS.values():
    ALL_SUPPORTED.update(exts)


class FileBrowser:
    def __init__(self, base_dir: Path = ASSETS_DIR):
        self._base_dir = base_dir

    def list_categories(self) -> list[str]:
        return [d.name for d in self._base_dir.iterdir() if d.is_dir()]

    def list_files(self, category: str = None) -> list[dict]:
        """List asset files, optionally filtered by category."""
        if category:
            search_dir = self._base_dir / category
            if not search_dir.is_dir():
                return []
            dirs = [search_dir]
        else:
            dirs = [d for d in self._base_dir.iterdir() if d.is_dir()]

        results = []
        for d in dirs:
            cat = d.name
            allowed = SUPPORTED_EXTENSIONS.get(cat, ALL_SUPPORTED)
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix.lower() in allowed:
                    results.append({
                        "name": f.name,
                        "category": cat,
                        "path": str(f.resolve()),
                        "size": f.stat().st_size,
                        "extension": f.suffix.lower(),
                    })
        return results

    def get_file_path(self, category: str, filename: str) -> Path:
        return self._base_dir / category / filename


file_browser = FileBrowser()
