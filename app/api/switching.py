from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.audio.auto_switcher import auto_switcher

router = APIRouter(prefix="/api/switching", tags=["switching"])


class AutoSwitchToggle(BaseModel):
    enabled: bool


class AutoSwitchConfig(BaseModel):
    threshold_db: Optional[float] = None
    debounce_ms: Optional[int] = None
    cooldown_ms: Optional[int] = None
    hysteresis_db: Optional[float] = None


@router.get("")
def get_state():
    return auto_switcher.get_state()


@router.post("/toggle")
def toggle(req: AutoSwitchToggle):
    auto_switcher.enabled = req.enabled
    return auto_switcher.get_state()


@router.post("/config")
def update_config(req: AutoSwitchConfig):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    auto_switcher.update_config(**updates)
    return auto_switcher.get_state()
