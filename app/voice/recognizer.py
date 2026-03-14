import json
import logging
import queue
import threading
from typing import Callable, Optional

import numpy as np

from app.config import config

logger = logging.getLogger(__name__)


class VoskRecognizer:
    """Always-listening speech recognizer on the producer's mic channel."""

    def __init__(self):
        self._model = None
        self._recognizer = None
        self._running = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._on_text_callbacks: list[Callable] = []

    def on_text(self, callback: Callable):
        self._on_text_callbacks.append(callback)

    def start(self) -> bool:
        if self._running:
            return True

        try:
            from vosk import Model, KaldiRecognizer
        except ImportError:
            logger.error("vosk not installed. Install with: pip install vosk")
            return False

        model_path = config.voice.model_path
        try:
            self._model = Model(model_path)
            self._recognizer = KaldiRecognizer(self._model, config.audio.sample_rate)
            self._running = True
            self._thread = threading.Thread(target=self._process_loop, daemon=True)
            self._thread.start()
            logger.info("Vosk recognizer started (model: %s)", model_path)
            return True
        except Exception as e:
            logger.error("Failed to start Vosk recognizer: %s", e)
            return False

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        self._model = None
        self._recognizer = None
        logger.info("Vosk recognizer stopped")

    def feed_audio(self, channel_data: np.ndarray):
        """Feed audio samples from the producer channel. Called from audio callback."""
        if self._running and not self._audio_queue.full():
            # Convert float32 [-1,1] to int16 for Vosk
            int16_data = (channel_data * 32767).astype(np.int16).tobytes()
            try:
                self._audio_queue.put_nowait(int16_data)
            except queue.Full:
                pass

    def _process_loop(self):
        while self._running:
            try:
                data = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self._recognizer.AcceptWaveform(data):
                result = json.loads(self._recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    logger.debug("Vosk recognized: '%s'", text)
                    for cb in self._on_text_callbacks:
                        try:
                            cb(text)
                        except Exception as e:
                            logger.error("Text callback error: %s", e)

    @property
    def running(self) -> bool:
        return self._running


vosk_recognizer = VoskRecognizer()
