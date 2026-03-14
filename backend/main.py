from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random, os, pathlib

from database import get_db, init_db

app = FastAPI(title="MindBridge API", version="1.0.0")

# ── CORS (allow frontend to talk to backend) ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: init DB ──────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("✅ MindBridge backend started!")
    print("📡 API docs: http://localhost:8000/docs")
    print("🌐 App:      http://localhost:8000")

# ── Serve frontend static files ───────────────────────────────────────────────
FRONTEND = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(str(FRONTEND / "index.html"))

@app.get("/{page}.html")
def serve_page(page: str):
    fp = FRONTEND / f"{page}.html"
    if fp.exists():
        return FileResponse(str(fp))
    raise HTTPException(404, "Page not found")

# ══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ══════════════════════════════════════════════════════════════════════════════

class MoodEntry(BaseModel):
    session_id: str          # anonymous browser ID
    mood: int                # 1–5
    label: str
    emoji: str
    note: Optional[str] = ""

class ChatMessage(BaseModel):
    session_id: str
    message: str

class CommunityPost(BaseModel):
    session_id: str
    content: str
    tag: Optional[str] = "General"

class PostVote(BaseModel):
    session_id: str

# ══════════════════════════════════════════════════════════════════════════════
# MOOD ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/mood")
def save_mood(entry: MoodEntry):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO moods (session_id, mood, label, emoji, note, created_at) VALUES (?,?,?,?,?,?)",
            (entry.session_id, entry.mood, entry.label, entry.emoji, entry.note, datetime.now().isoformat())
        )
        db.commit()

        # Calculate streak
        rows = db.execute(
            "SELECT created_at FROM moods WHERE session_id=? ORDER BY created_at DESC",
            (entry.session_id,)
        ).fetchall()

        streak = _calc_streak(rows)
        return {"success": True, "streak": streak, "message": "Mood saved!"}
    finally:
        db.close()


@app.get("/api/mood/{session_id}")
def get_moods(session_id: str, days: int = 30):
    db = get_db()
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = db.execute(
            "SELECT mood, label, emoji, note, created_at FROM moods WHERE session_id=? AND created_at>=? ORDER BY created_at DESC",
            (session_id, since)
        ).fetchall()
        moods = [{"mood": r[0], "label": r[1], "emoji": r[2], "note": r[3], "date": r[4]} for r in rows]

        # Stats
        if moods:
            avg = sum(m["mood"] for m in moods) / len(moods)
            streak = _calc_streak(db.execute(
                "SELECT created_at FROM moods WHERE session_id=? ORDER BY created_at DESC",
                (session_id,)
            ).fetchall())
        else:
            avg, streak = 0, 0

        return {"moods": moods, "avg": round(avg, 1), "streak": streak, "total": len(moods)}
    finally:
        db.close()


@app.get("/api/mood/stats/global")
def global_stats():
    """Anonymized platform-wide mood stats for the landing page."""
    db = get_db()
    try:
        total = db.execute("SELECT COUNT(*) FROM moods").fetchone()[0]
        avg   = db.execute("SELECT AVG(mood) FROM moods").fetchone()[0] or 0
        users = db.execute("SELECT COUNT(DISTINCT session_id) FROM moods").fetchone()[0]
        return {"total_checkins": total, "avg_mood": round(avg, 1), "total_users": users}
    finally:
        db.close()


def _calc_streak(rows):
    if not rows:
        return 0
    dates = sorted(set(r[0][:10] for r in rows), reverse=True)
    streak = 0
    today = datetime.now().date()
    for i, d in enumerate(dates):
        expected = (today - timedelta(days=i)).isoformat()
        if d == expected:
            streak += 1
        else:
            break
    return streak


# ══════════════════════════════════════════════════════════════════════════════
# AI CHAT ROUTES
# ══════════════════════════════════════════════════════════════════════════════

AI_RESPONSES = {
    "anxious": [
        "Anxiety can feel overwhelming, but you're already being brave by talking about it. 💚\n\nTry box breathing right now: breathe IN for 4 counts, HOLD 4, OUT for 6. Do it 3 times.\n\nWhat's making you anxious — is it something specific or a general feeling?",
        "That anxious feeling is your body trying to protect you, even if it doesn't help right now. You're not weak.\n\nCan you tell me more? Is it studies, relationships, the future, or something else?"
    ],
    "sleep": [
        "Sleep struggles are so common for students — and they make everything harder. 😔\n\nThings that genuinely help:\n• No screens 30 min before bed\n• Write down tomorrow's worries so your brain can let go\n• Same sleep time daily, even weekends\n\nIs your poor sleep linked to stress?",
    ],
    "exam": [
        "Exam stress is real — the pressure students carry is intense. 📚\n\nRemember: your worth is NOT your marks. One exam doesn't define your intelligence or your future.\n\nWhat's the biggest fear — failing, disappointing someone, or not knowing enough?",
    ],
    "lonely": [
        "Loneliness at college is more common than anyone admits — you're absolutely not alone. 💙\n\nSometimes loneliness comes even when we're surrounded by people, because connection feels shallow.\n\nIs there someone in your life you feel like you can't really talk to?",
    ],
    "family": [
        "Family pressure in India is unique and exhausting. The weight of expectations can feel suffocating. 😤\n\nIt's okay to love your family AND feel overwhelmed by their expectations. Both can be true at once.\n\nIs the pressure around career, marks, relationships?",
    ],
    "sad": [
        "I hear you. Sadness is heavy, and it's okay to sit with it for a moment. 💙\n\nYou don't have to fix the feeling immediately. Sometimes the most healing thing is to let yourself feel it.\n\nWhat happened — or has it been a slow build-up?",
    ],
    "crisis": [
        "I really hear what you're saying, and I'm very glad you told me. 💙\n\nWhat you're feeling is real — and you deserve real support right now.\n\n🚨 Please reach out to iCall: 9152987821 — it's free, confidential, and available today.\n\nWill you make that call? You don't have to face this alone.",
    ],
    "good": [
        "That's genuinely great to hear! 😊 Checking in when things are okay is actually excellent self-care.\n\nAnything on your mind — even something small? I'm here.",
        "Love to hear it! 💚 What's been making things feel good lately?",
    ],
    "default": [
        "Thank you for sharing that with me. It takes courage to put feelings into words. 💚\n\nCan you tell me a little more about what's been happening?",
        "I'm here and listening. What you're feeling is valid — no right or wrong emotion exists.\n\nWhat would help most right now — someone to talk to, coping techniques, or just space to vent?",
        "You're not alone in this. College can feel isolating even when it looks fine from outside.\n\nWhat's been the hardest part lately?",
        "That sounds really tough. You deserve support — not just from an AI, but from real people who care. 💚\n\nIs there a trusted person you could reach out to today?",
    ]
}

CRISIS_WORDS = ["suicide","kill myself","end it","don't want to live","want to die","no reason to live",
                "hopeless","self harm","hurt myself","give up on life","not worth living","end my life"]

def get_ai_response(text: str) -> tuple[str, bool]:
    """Returns (response_text, is_crisis)"""
    l = text.lower()
    is_crisis = any(w in l for w in CRISIS_WORDS)

    if is_crisis:
        return AI_RESPONSES["crisis"][0], True
    if any(w in l for w in ["anxi","stress","nervous","panic","worried","worry"]):
        return random.choice(AI_RESPONSES["anxious"]), False
    if any(w in l for w in ["sleep","insomnia","tired","exhausted","can't sleep"]):
        return random.choice(AI_RESPONSES["sleep"]), False
    if any(w in l for w in ["exam","study","marks","result","test","assignment","college"]):
        return random.choice(AI_RESPONSES["exam"]), False
    if any(w in l for w in ["lonely","alone","no friends","isolated","no one"]):
        return random.choice(AI_RESPONSES["lonely"]), False
    if any(w in l for w in ["family","parents","pressure","expectation","mom","dad"]):
        return random.choice(AI_RESPONSES["family"]), False
    if any(w in l for w in ["sad","cry","depress","unhappy","down","low","upset"]):
        return random.choice(AI_RESPONSES["sad"]), False
    if any(w in l for w in ["good","great","fine","okay","happy","better","well"]):
        return random.choice(AI_RESPONSES["good"]), False
    return random.choice(AI_RESPONSES["default"]), False


@app.post("/api/chat")
def chat(msg: ChatMessage):
    db = get_db()
    try:
        response, is_crisis = get_ai_response(msg.message)

        # Save both messages to DB
        now = datetime.now().isoformat()
        db.execute(
            "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
            (msg.session_id, "user", msg.message, now)
        )
        db.execute(
            "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
            (msg.session_id, "ai", response, now)
        )
        db.commit()

        return {"response": response, "is_crisis": is_crisis}
    finally:
        db.close()


@app.get("/api/chat/history/{session_id}")
def get_chat_history(session_id: str, limit: int = 50):
    db = get_db()
    try:
        rows = db.execute(
            "SELECT role, content, created_at FROM chat_messages WHERE session_id=? ORDER BY created_at ASC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        return {"messages": [{"role": r[0], "content": r[1], "time": r[2]} for r in rows]}
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
# COMMUNITY ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/community")
def create_post(post: CommunityPost):
    if len(post.content.strip()) < 5:
        raise HTTPException(400, "Post too short")
    if len(post.content) > 500:
        raise HTTPException(400, "Post too long (max 500 chars)")

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO community_posts (session_id, content, tag, upvotes, created_at) VALUES (?,?,?,0,?)",
            (post.session_id, post.content.strip(), post.tag, datetime.now().isoformat())
        )
        db.commit()
        return {"success": True, "post_id": cur.lastrowid}
    finally:
        db.close()


@app.get("/api/community")
def get_posts(limit: int = 30, tag: Optional[str] = None):
    db = get_db()
    try:
        if tag and tag != "All":
            rows = db.execute(
                "SELECT id, content, tag, upvotes, created_at FROM community_posts WHERE tag=? ORDER BY created_at DESC LIMIT ?",
                (tag, limit)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id, content, tag, upvotes, created_at FROM community_posts ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        posts = [{"id": r[0], "content": r[1], "tag": r[2], "upvotes": r[3], "date": r[4]} for r in rows]
        return {"posts": posts}
    finally:
        db.close()


@app.post("/api/community/{post_id}/upvote")
def upvote_post(post_id: int, vote: PostVote):
    db = get_db()
    try:
        # Check already voted
        existing = db.execute(
            "SELECT id FROM post_votes WHERE post_id=? AND session_id=?",
            (post_id, vote.session_id)
        ).fetchone()
        if existing:
            return {"success": False, "message": "Already voted"}

        db.execute("UPDATE community_posts SET upvotes=upvotes+1 WHERE id=?", (post_id,))
        db.execute("INSERT INTO post_votes (post_id, session_id) VALUES (?,?)", (post_id, vote.session_id))
        db.commit()

        new_count = db.execute("SELECT upvotes FROM community_posts WHERE id=?", (post_id,)).fetchone()[0]
        return {"success": True, "upvotes": new_count}
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    db = get_db()
    try:
        moods = db.execute("SELECT COUNT(*) FROM moods").fetchone()[0]
        posts = db.execute("SELECT COUNT(*) FROM community_posts").fetchone()[0]
        chats = db.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        return {
            "status": "healthy",
            "db": "connected",
            "stats": {"moods": moods, "posts": posts, "chat_messages": chats}
        }
    finally:
        db.close()
