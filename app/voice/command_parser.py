import logging
import time
from typing import Optional

from thefuzz import fuzz

from app.config import load_voice_commands

logger = logging.getLogger(__name__)


class CommandParser:
    def __init__(self):
        self._commands = load_voice_commands()
        self._threshold = self._commands.get("match_threshold", 0.70)
        self._cooldown = self._commands.get("cooldown_seconds", 2.0)
        self._last_command_time = 0.0
        self._last_command_text = ""

    def parse(self, text: str) -> Optional[dict]:
        """Try to match spoken text against known commands. Returns action dict or None."""
        now = time.time()
        if now - self._last_command_time < self._cooldown:
            return None

        text_lower = text.lower().strip()
        best_match = None
        best_score = 0.0

        for cmd in self._commands.get("commands", []):
            for phrase in cmd["phrases"]:
                score = fuzz.ratio(text_lower, phrase.lower()) / 100.0
                if score > best_score:
                    best_score = score
                    best_match = cmd

        if best_match and best_score >= self._threshold:
            self._last_command_time = now
            self._last_command_text = text
            result = {
                "action": best_match["action"],
                "params": best_match["params"],
                "matched_text": text,
                "confidence": best_score,
            }
            logger.info("Voice command: '%s' -> %s (%.0f%%)", text, result["action"], best_score * 100)
            return result

        logger.debug("No match for '%s' (best: %.0f%%)", text, best_score * 100)
        return None


command_parser = CommandParser()
