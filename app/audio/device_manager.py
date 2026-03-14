import logging
from typing import Optional

import sounddevice as sd

from app.config import config

logger = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self):
        self._device_index: Optional[int] = None
        self._device_info: Optional[dict] = None

    def find_scarlett(self) -> Optional[int]:
        """Find the Scarlett 18i20 by name in WASAPI devices."""
        target = config.audio.device_name
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if target.lower() in dev["name"].lower() and dev["max_input_channels"] >= config.audio.num_channels:
                # Prefer WASAPI host API on Windows
                hostapi = sd.query_hostapis(dev["hostapi"])
                if "wasapi" in hostapi["name"].lower() or "windows audio" in hostapi["name"].lower():
                    self._device_index = i
                    self._device_info = dev
                    logger.info("Found Scarlett: device %d '%s' (%d channels, %s)",
                                i, dev["name"], dev["max_input_channels"], hostapi["name"])
                    return i

        # Fallback: accept any matching device regardless of host API
        for i, dev in enumerate(devices):
            if target.lower() in dev["name"].lower() and dev["max_input_channels"] >= config.audio.num_channels:
                self._device_index = i
                self._device_info = dev
                logger.info("Found Scarlett (fallback): device %d '%s' (%d channels)",
                            i, dev["name"], dev["max_input_channels"])
                return i

        logger.warning("Scarlett '%s' not found. Available input devices:", target)
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                logger.warning("  [%d] %s (%d ch)", i, dev["name"], dev["max_input_channels"])
        return None

    def list_input_devices(self) -> list[dict]:
        """List all available input devices."""
        devices = sd.query_devices()
        result = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                hostapi = sd.query_hostapis(dev["hostapi"])
                result.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "sample_rate": dev["default_samplerate"],
                    "host_api": hostapi["name"],
                })
        return result

    @property
    def device_index(self) -> Optional[int]:
        return self._device_index

    @property
    def device_info(self) -> Optional[dict]:
        return self._device_info


device_manager = DeviceManager()
