import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Anime, Episode

app = FastAPI(title="Anime API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Anime API is running"}

# Utility to convert ObjectId fields to string

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id")) if doc.get("_id") else None
    # convert any nested ObjectId
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

# Seed minimal demo data if empty
@app.on_event("startup")
async def seed_if_empty():
    try:
        if db is None:
            return
        if db["anime"].count_documents({}) == 0:
            a_id = db["anime"].insert_one({
                "title": "Demo: Ninja Chronicles",
                "description": "A young ninja embarks on a journey.",
                "cover_url": "https://images.unsplash.com/photo-1546443046-ed1ce6ffd1dc?q=80&w=1200&auto=format&fit=crop",
                "tags": ["action", "adventure"],
                "year": 2020
            }).inserted_id
            db["episode"].insert_many([
                {"anime_id": str(a_id), "number": 1, "title": "A New Path", "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "thumbnail_url": "https://picsum.photos/seed/ep1/600/338", "duration": 10},
                {"anime_id": str(a_id), "number": 2, "title": "Training Days", "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", "thumbnail_url": "https://picsum.photos/seed/ep2/600/338", "duration": 12},
                {"anime_id": str(a_id), "number": 3, "title": "First Mission", "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4", "thumbnail_url": "https://picsum.photos/seed/ep3/600/338", "duration": 14},
            ])
    except Exception:
        # ignore seeding errors in ephemeral env
        pass

# Schemas for responses
class AnimeOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    tags: Optional[List[str]] = []
    year: Optional[int] = None

class EpisodeOut(BaseModel):
    id: str
    anime_id: str
    number: int
    title: str
    stream_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None

# Endpoints
@app.get("/api/anime", response_model=List[AnimeOut])
def list_anime(q: Optional[str] = None):
    if db is None:
        return []
    query = {"title": {"$regex": q, "$options": "i"}} if q else {}
    items = list(db["anime"].find(query).sort("title"))
    return [serialize_doc(x) for x in items]

@app.post("/api/anime", response_model=str)
def create_anime(payload: Anime):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    _id = create_document("anime", payload)
    return _id

@app.get("/api/anime/{anime_id}", response_model=AnimeOut)
def get_anime(anime_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["anime"].find_one({"_id": ObjectId(anime_id)}) if ObjectId.is_valid(anime_id) else db["anime"].find_one({"_id": anime_id})
    if not doc:
        raise HTTPException(404, "Anime not found")
    return serialize_doc(doc)

@app.get("/api/anime/{anime_id}/episodes", response_model=List[EpisodeOut])
def list_episodes(anime_id: str):
    if db is None:
        return []
    items = list(db["episode"].find({"anime_id": anime_id}).sort("number"))
    return [serialize_doc(x) for x in items]

@app.post("/api/anime/{anime_id}/episodes", response_model=str)
def create_episode(anime_id: str, payload: Episode):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    data = payload.model_dump()
    data["anime_id"] = anime_id
    _id = create_document("episode", data)
    return _id

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
