from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.assets.file_browser import file_browser
from app.assets.asset_loader import asset_loader

router = APIRouter(prefix="/api/assets", tags=["assets"])


class LoadRequest(BaseModel):
    file_path: str
    scene_name: Optional[str] = None
    input_name: Optional[str] = None


class RemoveRequest(BaseModel):
    input_name: str


@router.get("")
def list_assets(category: str = None):
    files = file_browser.list_files(category)
    categories = file_browser.list_categories()
    return {"files": files, "categories": categories}


@router.post("/load")
def load_asset(req: LoadRequest):
    result = asset_loader.load_to_scene(req.file_path, req.scene_name, req.input_name)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    return result


@router.post("/remove")
def remove_asset(req: RemoveRequest):
    result = asset_loader.remove_from_scene(req.input_name)
    return result
