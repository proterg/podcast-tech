import logging
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

from app.config import config
from app.audio.device_manager import device_manager

logger = logging.getLogger(__name__)


class LevelMonitor:
    """Reads multi-channel audio from Scarlett and computes per-channel RMS levels."""

    def __init__(self):
        self._stream: Optional[sd.InputStream] = None
        self._running = False
        self._levels_db: np.ndarray = np.full(config.audio.num_channels, -100.0)
        self._lock = threading.Lock()
        self._callbacks: list[Callable] = []

    @property
    def levels_db(self) -> list[float]:
        with self._lock:
            return self._levels_db.tolist()

    def on_levels(self, callback: Callable):
        self._callbacks.append(callback)

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        if status:
            logger.warning("Audio status: %s", status)

        num_ch = min(indata.shape[1], config.audio.num_channels)
        rms = np.sqrt(np.mean(indata[:, :num_ch] ** 2, axis=0))
        # Convert to dB, floor at -100
        with np.errstate(divide="ignore"):
            db = 20 * np.log10(np.maximum(rms, 1e-10))

        with self._lock:
            self._levels_db[:num_ch] = db

        for cb in self._callbacks:
            try:
                cb(db[:num_ch].tolist())
            except Exception as e:
                logger.error("Level callback error: %s", e)

    def start(self) -> bool:
        idx = device_manager.device_index
        if idx is None:
            idx = device_manager.find_scarlett()
        if idx is None:
            logger.error("Cannot start level monitor: no audio device found")
            return False

        try:
            self._stream = sd.InputStream(
                device=idx,
                channels=config.audio.num_channels,
                samplerate=config.audio.sample_rate,
                blocksize=config.audio.block_size,
                dtype="float32",
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            logger.info("Level monitor started (device %d, %d channels, %d Hz)",
                        idx, config.audio.num_channels, config.audio.sample_rate)
            return True
        except Exception as e:
            logger.error("Failed to start level monitor: %s", e)
            return False

    def stop(self):
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
            logger.info("Level monitor stopped")

    @property
    def running(self) -> bool:
        return self._running


level_monitor = LevelMonitor()
