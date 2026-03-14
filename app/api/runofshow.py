import uuid
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.config import load_runofshow, save_runofshow, ASSETS_DIR

router = APIRouter(prefix="/api/runofshow", tags=["runofshow"])


class AssetRef(BaseModel):
    path: str
    name: str = ""


class Segment(BaseModel):
    id: str
    label: str
    title: str = ""
    notes: str = ""
    assets: list[AssetRef] = []


class RunOfShowUpdate(BaseModel):
    segments: list[Segment]


class SegmentCreate(BaseModel):
    label: str
    title: str = ""
    notes: str = ""


@router.get("")
def get_runofshow():
    return load_runofshow()


@router.post("")
def save_all(update: RunOfShowUpdate):
    data = {"segments": [s.model_dump() for s in update.segments]}
    save_runofshow(data)
    return data


@router.post("/segment")
def add_segment(req: SegmentCreate):
    data = load_runofshow()
    segment = {
        "id": uuid.uuid4().hex[:8],
        "label": req.label,
        "title": req.title,
        "notes": req.notes,
        "assets": [],
    }
    # Insert before Outro if it exists, otherwise append
    segments = data["segments"]
    outro_idx = next((i for i, s in enumerate(segments) if s.get("label", "").upper() == "OUTRO"), None)
    if outro_idx is not None:
        segments.insert(outro_idx, segment)
    else:
        segments.append(segment)
    save_runofshow(data)
    return data


@router.delete("/segment/{segment_id}")
def delete_segment(segment_id: str):
    data = load_runofshow()
    data["segments"] = [s for s in data["segments"] if s["id"] != segment_id]
    save_runofshow(data)
    return data


@router.post("/upload/{segment_id}")
async def upload_asset(segment_id: str, file: UploadFile = File(...)):
    """Upload a file to assets/ and attach it to a segment."""
    # Save file to assets directory
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    dest = ASSETS_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Add to segment
    data = load_runofshow()
    for seg in data["segments"]:
        if seg["id"] == segment_id:
            if "assets" not in seg:
                seg["assets"] = []
            # Don't add duplicates
            if not any(a["path"] == str(dest) for a in seg["assets"]):
                seg["assets"].append({"path": str(dest), "name": file.filename})
            save_runofshow(data)
            return {"success": True, "segment": seg}

    raise HTTPException(status_code=404, detail=f"Segment {segment_id} not found")
