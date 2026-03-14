from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.obs.scene_manager import scene_manager
from app.obs.scene_builder import scene_builder

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


class SwitchRequest(BaseModel):
    scene: str


class BuildRequest(BaseModel):
    template: str
    scene_name: Optional[str] = None


class LowerThirdRequest(BaseModel):
    name: str
    title: str = ""


@router.get("")
def list_scenes():
    scenes = scene_manager.get_scene_list()
    current = scene_manager.get_current_scene()
    return {"scenes": scenes, "current": current}


@router.post("/switch")
def switch_scene(req: SwitchRequest):
    success = scene_manager.switch_scene(req.scene)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to switch to '{req.scene}'")
    return {"success": True, "scene": req.scene}


@router.get("/templates")
def list_templates():
    return {"templates": scene_builder.get_templates()}


@router.post("/build")
def build_scene(req: BuildRequest):
    success = scene_builder.build_scene(req.template, req.scene_name)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to build scene from template '{req.template}'")
    return {"success": True, "template": req.template}


@router.post("/lower-third")
def show_lower_third(req: LowerThirdRequest):
    success = scene_builder.build_lower_third_scene(req.name, req.title)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create lower third")
    return {"success": True}


@router.delete("/lower-third")
def hide_lower_third():
    success = scene_builder.hide_lower_third()
    return {"success": success}
