// ── MindBridge API Client ─────────────────────────────────────────────────
const API = "http://localhost:8000/api";

// Generate or retrieve anonymous session ID
function getSessionId() {
  let sid = localStorage.getItem("mb_session");
  if (!sid) {
    sid = "mb_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem("mb_session", sid);
  }
  return sid;
}

const SESSION = getSessionId();

// Generic fetch wrapper
async function apiFetch(path, method = "GET", body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// Mood API
const MoodAPI = {
  save: (mood, label, emoji, note) =>
    apiFetch("/mood", "POST", { session_id: SESSION, mood, label, emoji, note }),
  history: (days = 30) => apiFetch(`/mood/${SESSION}?days=${days}`),
  globalStats: () => apiFetch("/mood/stats/global"),
};

// Chat API
const ChatAPI = {
  send: (message) =>
    apiFetch("/chat", "POST", { session_id: SESSION, message }),
  history: () => apiFetch(`/chat/history/${SESSION}`),
};

// Community API
const CommunityAPI = {
  getPosts: (tag = "All") =>
    apiFetch(`/community${tag !== "All" ? "?tag=" + tag : ""}`),
  createPost: (content, tag) =>
    apiFetch("/community", "POST", { session_id: SESSION, content, tag }),
  upvote: (postId) =>
    apiFetch(`/community/${postId}/upvote`, "POST", { session_id: SESSION }),
};
