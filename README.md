# 🧠 MindBridge — Full Stack Mental Health App

**Tech Stack:** Python · FastAPI · SQLite · HTML/CSS/JavaScript

---

## 🚀 Quick Start (One Command)

```bash
python run.py
```

Then open **http://localhost:8000** in your browser. That's it!

---

## 📁 Project Structure

```
mindbridge/
├── run.py                  ← START HERE — runs everything
├── backend/
│   ├── main.py             ← All API routes (FastAPI)
│   ├── database.py         ← SQLite setup & queries
│   ├── requirements.txt    ← Python packages
│   └── mindbridge.db       ← Auto-created database file
└── frontend/
    ├── api.js              ← Shared API client (used by all pages)
    ├── index.html          ← Landing page
    ├── checkin.html        ← Daily mood check-in
    ├── chat.html           ← AI chat support
    ├── tracker.html        ← Mood history & chart
    ├── resources.html      ← Helplines & self-help
    └── community.html      ← Anonymous peer board
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/mood` | Save mood check-in |
| `GET` | `/api/mood/{session_id}?days=7` | Get mood history |
| `GET` | `/api/mood/stats/global` | Platform-wide stats |
| `POST` | `/api/chat` | Send message, get AI response |
| `GET` | `/api/chat/history/{session_id}` | Load chat history |
| `POST` | `/api/community` | Create anonymous post |
| `GET` | `/api/community?tag=Anxiety` | Get community posts |
| `POST` | `/api/community/{id}/upvote` | Upvote a post |
| `GET` | `/api/health` | Server health check |
| `GET` | `/docs` | Interactive API docs (Swagger UI) |

---

## ⚙️ Manual Setup (if run.py doesn't work)

```bash
# 1. Install Python 3.9+
# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload --port 8000

# 4. Open browser
# http://localhost:8000
```

---

## 🏆 Features

- ✅ **Daily Mood Check-in** — 5-level emoji selector + optional note
- ✅ **Mood Tracker** — Line chart (7/14/30 day views) powered by Chart.js
- ✅ **AI Chat Support** — Context-aware responses + crisis detection
- ✅ **Crisis Detection** — Keywords trigger emergency helpline banner
- ✅ **Anonymous Community Board** — Post, filter by tag, upvote
- ✅ **Resources Page** — Real Indian helplines with click-to-call
- ✅ **Session-based** — No login, no signup, fully anonymous
- ✅ **Streak Tracking** — Calculated server-side, persisted in SQLite
- ✅ **Live Stats** — Homepage shows real check-in counts from DB

---

## 📞 Crisis Helplines (India)

| Organisation | Number | Availability |
|---|---|---|
| iCall (TISS) | 9152987821 | Mon–Sat 8am–10pm |
| Vandrevala Foundation | 1860-2662-345 | 24/7 |
| Snehi Foundation | 044-24640050 | Available |

---

## 🛡️ Privacy

- Zero login or signup required
- Session IDs are randomly generated — not linked to any personal data
- All data stored locally in `backend/mindbridge.db`
- No data sent to any third-party service
