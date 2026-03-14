import logging
import secrets
import string
from typing import Optional

from app.obs.connection import obs_connection
from app.obs.source_manager import source_manager

logger = logging.getLogger(__name__)

VDONINJA_BASE = "https://vdo.ninja"
MAX_SLOTS = 2


def _random_id(length: int = 8) -> str:
    return "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class CallInSlot:
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.stream_id: str = ""
        self.room_id: str = ""
        self.password: str = ""
        self.guest_name: str = ""
        self.active: bool = False
        self.obs_source_name: str = f"Call-In {slot_id}"

    @property
    def guest_url(self) -> str:
        """URL the remote guest opens in their browser to send video/audio."""
        params = (
            f"push={self.stream_id}"
            f"&room={self.room_id}"
            f"&password={self.password}"
            f"&webcam&autostart"
            f"&label={self.guest_name or f'Guest {self.slot_id}'}"
        )
        return f"{VDONINJA_BASE}/?{params}"

    @property
    def obs_view_url(self) -> str:
        """URL for OBS Browser Source to receive the guest's feed."""
        params = (
            f"view={self.stream_id}"
            f"&room={self.room_id}"
            f"&password={self.password}"
            f"&solo&cleanoutput"
            f"&nocontrols"
        )
        return f"{VDONINJA_BASE}/?{params}"

    def to_dict(self) -> dict:
        return {
            "slot_id": self.slot_id,
            "stream_id": self.stream_id,
            "room_id": self.room_id,
            "guest_name": self.guest_name,
            "active": self.active,
            "guest_url": self.guest_url if self.stream_id else "",
            "obs_source_name": self.obs_source_name,
        }


class CallInManager:
    """Manages up to 2 VDO.Ninja call-in slots as OBS Browser Sources."""

    def __init__(self):
        self.slots: list[CallInSlot] = [CallInSlot(i + 1) for i in range(MAX_SLOTS)]

    def create_invite(self, slot_id: int, guest_name: str = "") -> Optional[dict]:
        """Generate a fresh VDO.Ninja invite for a slot."""
        slot = self._get_slot(slot_id)
        if not slot:
            return None

        # Generate unique IDs for this session
        session_id = _random_id(10)
        slot.stream_id = f"uncapped_s{slot_id}_{session_id}"
        slot.room_id = f"uncapped_{session_id}"
        slot.password = _random_id(6)
        slot.guest_name = guest_name or f"Guest {slot_id}"
        slot.active = False  # Not active in OBS yet, just invite created

        logger.info("Created call-in invite for slot %d: %s", slot_id, slot.guest_name)
        return slot.to_dict()

    def activate_slot(self, slot_id: int) -> Optional[dict]:
        """Create the OBS Browser Source for this call-in slot."""
        slot = self._get_slot(slot_id)
        if not slot or not slot.stream_id:
            return None

        client = obs_connection.client
        if not client:
            logger.error("OBS not connected")
            return None

        # Remove existing source if present
        try:
            source_manager.remove_input(slot.obs_source_name)
        except Exception:
            pass

        # Create browser source pointing to VDO.Ninja view URL
        try:
            current_scene = client.get_current_program_scene().scene_name
            item_id = source_manager.create_input(
                current_scene,
                slot.obs_source_name,
                "browser_source",
                {
                    "url": slot.obs_view_url,
                    "width": 1920,
                    "height": 1080,
                    "css": "",
                    "reroute_audio": True,
                },
                enabled=True,
            )
            if item_id is not None:
                slot.active = True
                logger.info("Activated call-in slot %d in scene '%s'", slot_id, current_scene)
                return slot.to_dict()
        except Exception as e:
            logger.error("Failed to activate call-in slot %d: %s", slot_id, e)

        return None

    def deactivate_slot(self, slot_id: int) -> Optional[dict]:
        """Remove the OBS Browser Source for this call-in slot."""
        slot = self._get_slot(slot_id)
        if not slot:
            return None

        try:
            source_manager.remove_input(slot.obs_source_name)
        except Exception:
            pass

        slot.active = False
        logger.info("Deactivated call-in slot %d", slot_id)
        return slot.to_dict()

    def clear_slot(self, slot_id: int) -> Optional[dict]:
        """Fully reset a slot - remove source and clear invite."""
        slot = self._get_slot(slot_id)
        if not slot:
            return None

        if slot.active:
            self.deactivate_slot(slot_id)

        slot.stream_id = ""
        slot.room_id = ""
        slot.password = ""
        slot.guest_name = ""
        slot.active = False

        logger.info("Cleared call-in slot %d", slot_id)
        return slot.to_dict()

    def get_slots(self) -> list[dict]:
        return [s.to_dict() for s in self.slots]

    def add_to_scene(self, slot_id: int, scene_name: str,
                     x: float = 0, y: float = 0,
                     width: float = 1920, height: float = 1080) -> bool:
        """Add an active call-in source to a specific scene with positioning."""
        slot = self._get_slot(slot_id)
        if not slot or not slot.active:
            return False

        item_id = source_manager.add_existing_source(scene_name, slot.obs_source_name)
        if item_id is not None:
            source_manager.set_item_transform(scene_name, item_id, x, y, width, height)
            return True
        return False

    def _get_slot(self, slot_id: int) -> Optional[CallInSlot]:
        if 1 <= slot_id <= MAX_SLOTS:
            return self.slots[slot_id - 1]
        logger.error("Invalid slot ID: %d (max %d)", slot_id, MAX_SLOTS)
        return None


callin_manager = CallInManager()
