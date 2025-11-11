import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document
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
    doc = dict(doc)
    if doc.get("_id"):
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = None
    # convert any nested ObjectId
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

# -------- Demo fallback (when database is not configured) --------
DEMO_ANIME: List[dict] = []
DEMO_EPISODES: List[dict] = []

def build_demo_data():
    global DEMO_ANIME, DEMO_EPISODES
    if DEMO_ANIME and DEMO_EPISODES:
        return
    demo_anime_seed = [
        {
            "id": "demo-1",
            "title": "Big Brother",
            "description": "A tournament of wits and strength across a futuristic city.",
            "cover_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?q=80&w=1200&auto=format&fit=crop",
            "tags": ["drama", "sci-fi"],
            "year": 2021,
        },
        {
            "id": "demo-2",
            "title": "A Will Eternal",
            "description": "A cultivator seeks immortality through perseverance and heart.",
            "cover_url": "https://images.unsplash.com/photo-1520975922284-9d78175cfea0?q=80&w=1200&auto=format&fit=crop",
            "tags": ["fantasy", "adventure"],
            "year": 2020,
        },
        {
            "id": "demo-3",
            "title": "Over Goddess",
            "description": "A fallen deity walks the mortal world in search of purpose.",
            "cover_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
            "tags": ["supernatural", "romance"],
            "year": 2019,
        },
        {
            "id": "demo-4",
            "title": "The Demon Hunter",
            "description": "A lone hunter tracks demonic entities lurking in the shadows.",
            "cover_url": "https://images.unsplash.com/photo-1503342452485-86ff0a8bccc5?q=80&w=1200&auto=format&fit=crop",
            "tags": ["action", "dark fantasy"],
            "year": 2022,
        },
        {
            "id": "demo-5",
            "title": "X Epoch Of Dragon",
            "description": "Dragon heirs awaken to reshape an ancient world.",
            "cover_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
            "tags": ["epic", "mythology"],
            "year": 2023,
        },
    ]

    sample_videos = [
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "thumb": "https://picsum.photos/seed/ep1/600/338",
            "title": "Pilot",
            "duration": 10,
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "thumb": "https://picsum.photos/seed/ep2/600/338",
            "title": "Awakening",
            "duration": 12,
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "thumb": "https://picsum.photos/seed/ep3/600/338",
            "title": "Crossroads",
            "duration": 14,
        },
    ]

    DEMO_ANIME = [serialize_doc(a) for a in demo_anime_seed]
    eps: List[dict] = []
    for a in DEMO_ANIME:
        for idx, vid in enumerate(sample_videos, start=1):
            eps.append(serialize_doc({
                "id": f"{a['id']}-ep-{idx}",
                "anime_id": a["id"],
                "number": idx,
                "title": f"{a['title']} - {vid['title']}",
                "stream_url": vid["url"],
                "thumbnail_url": vid["thumb"],
                "duration": vid["duration"],
            }))
    DEMO_EPISODES = eps

# Seed demo content if collections are empty
@app.on_event("startup")
async def seed_if_empty():
    try:
        # If no database configured, prepare demo fallback
        if db is None:
            build_demo_data()
            return
        if db["anime"].count_documents({}) == 0:
            demo_anime = [
                {
                    "title": "Big Brother",
                    "description": "A tournament of wits and strength across a futuristic city.",
                    "cover_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["drama", "sci-fi"],
                    "year": 2021,
                },
                {
                    "title": "A Will Eternal",
                    "description": "A cultivator seeks immortality through perseverance and heart.",
                    "cover_url": "https://images.unsplash.com/photo-1520975922284-9d78175cfea0?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["fantasy", "adventure"],
                    "year": 2020,
                },
                {
                    "title": "Over Goddess",
                    "description": "A fallen deity walks the mortal world in search of purpose.",
                    "cover_url": "https://images.unsplash.com/photo-1519681393784-9d78175cfea0?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["supernatural", "romance"],
                    "year": 2019,
                },
                {
                    "title": "The Demon Hunter",
                    "description": "A lone hunter tracks demonic entities lurking in the shadows.",
                    "cover_url": "https://images.unsplash.com/photo-1503342452485-86ff0a8bccc5?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["action", "dark fantasy"],
                    "year": 2022,
                },
                {
                    "title": "X Epoch Of Dragon",
                    "description": "Dragon heirs awaken to reshape an ancient world.",
                    "cover_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["epic", "mythology"],
                    "year": 2023,
                },
            ]

            sample_videos = [
                {
                    "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    "thumb": "https://picsum.photos/seed/ep1/600/338",
                    "title": "Pilot",
                    "duration": 10,
                },
                {
                    "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                    "thumb": "https://picsum.photos/seed/ep2/600/338",
                    "title": "Awakening",
                    "duration": 12,
                },
                {
                    "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                    "thumb": "https://picsum.photos/seed/ep3/600/338",
                    "title": "Crossroads",
                    "duration": 14,
                },
            ]

            for a in demo_anime:
                a_id = db["anime"].insert_one(a).inserted_id
                eps = []
                for idx, vid in enumerate(sample_videos, start=1):
                    eps.append({
                        "anime_id": str(a_id),
                        "number": idx,
                        "title": f"{a['title']} - {vid['title']}",
                        "stream_url": vid["url"],
                        "thumbnail_url": vid["thumb"],
                        "duration": vid["duration"],
                    })
                db["episode"].insert_many(eps)
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
    # Fallback to demo data when DB is not configured
    if db is None:
        build_demo_data()
        items = DEMO_ANIME
        if q:
            items = [a for a in items if q.lower() in a["title"].lower()]
        items = sorted(items, key=lambda x: x.get("title", ""))
        return items
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
        build_demo_data()
        found = next((a for a in DEMO_ANIME if a["id"] == anime_id), None)
        if not found:
            raise HTTPException(404, "Anime not found")
        return found
    doc = db["anime"].find_one({"_id": ObjectId(anime_id)}) if ObjectId.is_valid(anime_id) else db["anime"].find_one({"_id": anime_id})
    if not doc:
        raise HTTPException(404, "Anime not found")
    return serialize_doc(doc)

@app.get("/api/anime/{anime_id}/episodes", response_model=List[EpisodeOut])
def list_episodes(anime_id: str):
    if db is None:
        build_demo_data()
        items = [e for e in DEMO_EPISODES if e["anime_id"] == anime_id]
        items = sorted(items, key=lambda x: x.get("number", 0))
        return items
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
    if db is None:
        response["demo_data"] = True
        response["demo_counts"] = {
            "anime": len(DEMO_ANIME),
            "episodes": len(DEMO_EPISODES)
        }
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
