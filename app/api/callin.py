from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.callin.manager import callin_manager

router = APIRouter(prefix="/api/callin", tags=["callin"])


class InviteRequest(BaseModel):
    slot_id: int
    guest_name: str = ""


class SlotRequest(BaseModel):
    slot_id: int


class AddToSceneRequest(BaseModel):
    slot_id: int
    scene_name: str
    x: float = 0
    y: float = 0
    width: float = 1920
    height: float = 1080


@router.get("")
def get_slots():
    return {"slots": callin_manager.get_slots()}


@router.post("/invite")
def create_invite(req: InviteRequest):
    result = callin_manager.create_invite(req.slot_id, req.guest_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Invalid slot ID: {req.slot_id}")
    return result


@router.post("/activate")
def activate_slot(req: SlotRequest):
    result = callin_manager.activate_slot(req.slot_id)
    if not result:
        raise HTTPException(status_code=500, detail=f"Failed to activate slot {req.slot_id}")
    return result


@router.post("/deactivate")
def deactivate_slot(req: SlotRequest):
    result = callin_manager.deactivate_slot(req.slot_id)
    if not result:
        raise HTTPException(status_code=400, detail=f"Invalid slot ID: {req.slot_id}")
    return result


@router.post("/clear")
def clear_slot(req: SlotRequest):
    result = callin_manager.clear_slot(req.slot_id)
    if not result:
        raise HTTPException(status_code=400, detail=f"Invalid slot ID: {req.slot_id}")
    return result


@router.post("/add-to-scene")
def add_to_scene(req: AddToSceneRequest):
    success = callin_manager.add_to_scene(
        req.slot_id, req.scene_name, req.x, req.y, req.width, req.height
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add call-in to scene")
    return {"success": True}
