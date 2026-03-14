import logging
import time
import threading
from typing import Optional

from app.config import config, load_mic_mapping
from app.obs.scene_manager import scene_manager

logger = logging.getLogger(__name__)


class AutoSwitcher:
    """Switches camera based on who's talking. Uses debounce, cooldown, hysteresis, priority."""

    def __init__(self):
        self._enabled = False
        self._lock = threading.Lock()
        self._mic_mapping = load_mic_mapping()
        self._channels = self._mic_mapping["channels"]

        # State
        self._current_camera: Optional[str] = None
        self._current_speaker_db: float = -100.0
        self._candidate_camera: Optional[str] = None
        self._candidate_start: float = 0.0
        self._last_switch_time: float = 0.0
        self._multi_speaker_start: float = 0.0

        # Config shortcuts
        self._cfg = config.auto_switch

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        if value:
            self._current_camera = scene_manager.get_current_scene()
            logger.info("Auto-switch enabled (current: %s)", self._current_camera)
        else:
            logger.info("Auto-switch disabled")

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._cfg, key):
                setattr(self._cfg, key, value)

    def process_levels(self, levels_db: list[float]):
        """Called with per-channel dB levels. Decides whether to switch."""
        if not self._enabled:
            return

        now = time.time()

        with self._lock:
            threshold = self._cfg.threshold_db

            # Find active channels (above threshold), excluding producer (channel 6)
            active = []
            for ch_info in self._channels:
                ch = ch_info["channel"]
                if ch >= len(levels_db) or ch_info["camera"] is None:
                    continue
                if levels_db[ch] > threshold:
                    active.append({
                        "channel": ch,
                        "camera": ch_info["camera"],
                        "priority": ch_info["priority"],
                        "db": levels_db[ch],
                    })

            # Multi-speaker detection: 3+ active channels -> Gallery
            if len(active) >= self._cfg.gallery_trigger_channels:
                if self._multi_speaker_start == 0:
                    self._multi_speaker_start = now
                elif (now - self._multi_speaker_start) * 1000 >= self._cfg.gallery_trigger_ms:
                    self._try_switch("Gallery", now)
                    self._multi_speaker_start = 0
                return
            else:
                self._multi_speaker_start = 0

            if not active:
                self._candidate_camera = None
                return

            # Deduplicate by camera (e.g., channels 2+3 both map to Camera 3)
            camera_best = {}
            for a in active:
                cam = a["camera"]
                if cam not in camera_best or a["db"] > camera_best[cam]["db"]:
                    camera_best[cam] = a

            # Pick loudest camera, with priority as tiebreaker
            candidates = sorted(camera_best.values(), key=lambda x: (-x["db"], x["priority"]))
            best = candidates[0]

            # Hysteresis: new speaker must be louder than current by hysteresis_db
            if (self._current_camera and best["camera"] != self._current_camera
                    and best["db"] < self._current_speaker_db + self._cfg.hysteresis_db):
                return

            target_camera = best["camera"]

            # Same camera already showing?
            if target_camera == self._current_camera:
                self._current_speaker_db = best["db"]
                self._candidate_camera = None
                return

            # Debounce: must sustain for debounce_ms
            if target_camera != self._candidate_camera:
                self._candidate_camera = target_camera
                self._candidate_start = now
                return

            elapsed_ms = (now - self._candidate_start) * 1000
            if elapsed_ms < self._cfg.debounce_ms:
                return

            self._try_switch(target_camera, now)
            self._current_speaker_db = best["db"]

    def _try_switch(self, camera: str, now: float):
        """Switch if cooldown has elapsed."""
        cooldown_ms = self._cfg.cooldown_ms
        if (now - self._last_switch_time) * 1000 < cooldown_ms:
            return

        if scene_manager.switch_scene(camera):
            self._current_camera = camera
            self._last_switch_time = now
            self._candidate_camera = None
            logger.info("Auto-switched to %s", camera)

    def get_state(self) -> dict:
        return {
            "enabled": self._enabled,
            "current_camera": self._current_camera,
            "threshold_db": self._cfg.threshold_db,
            "debounce_ms": self._cfg.debounce_ms,
            "cooldown_ms": self._cfg.cooldown_ms,
            "hysteresis_db": self._cfg.hysteresis_db,
        }


auto_switcher = AutoSwitcher()
