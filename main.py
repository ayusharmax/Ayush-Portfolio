import os
import sqlite3
import secrets
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "portfolio.db"))
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

app = FastAPI(
    title="Ayush Sharma Portfolio API",
    description="Backend API for Ayush Sharma's portfolio website",
    version="1.0.0",
)

@contextmanager
def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tech_stack TEXT NOT NULL DEFAULT '',
                project_url TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

@app.on_event("startup")
def on_startup():
    init_db()

class ContactMessage(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=10, max_length=3000)

class ProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1000)
    tech_stack: str = Field(default="", max_length=300)
    project_url: str = Field(default="", max_length=500)

def require_admin(x_admin_key: Optional[str] = Header(default=None)):
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are disabled. Set the ADMIN_API_KEY environment variable first."
        )
    if not x_admin_key or not secrets.compare_digest(x_admin_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Ayush Sharma Portfolio API"}

@app.post("/api/contact", status_code=201)
def submit_contact(payload: ContactMessage):
    name = payload.name.strip()
    email = str(payload.email).strip()
    subject = payload.subject.strip()
    message = payload.message.strip()
    if not name or not subject or not message:
        raise HTTPException(status_code=422, detail="Please complete all fields.")
    with db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
            (name, email, subject, message),
        )
        message_id = cursor.lastrowid
    return {"ok": True, "message": "Thanks! Your message has been saved.", "id": message_id}

@app.get("/api/projects")
def list_projects():
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, description, tech_stack, project_url, created_at FROM projects ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]

@app.post("/api/admin/projects", status_code=201, dependencies=[Depends(require_admin)])
def create_project(payload: ProjectCreate):
    with db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO projects (title, description, tech_stack, project_url) VALUES (?, ?, ?, ?)",
            (payload.title.strip(), payload.description.strip(), payload.tech_stack.strip(), payload.project_url.strip()),
        )
        project_id = cursor.lastrowid
    return {"ok": True, "id": project_id}

@app.get("/api/admin/messages", dependencies=[Depends(require_admin)])
def list_messages():
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, subject, message, created_at FROM messages ORDER BY id DESC LIMIT 200"
        ).fetchall()
    return [dict(row) for row in rows]

@app.delete("/api/admin/messages/{message_id}", dependencies=[Depends(require_admin)])
def delete_message(message_id: int):
    with db_connection() as conn:
        cursor = conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Message not found.")
    return {"ok": True, "deleted_id": message_id}

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")
@app.get("/resume", include_in_schema=False)
@app.get("/resume.html", include_in_schema=False)
def resume():
    return FileResponse(STATIC_DIR / "resume.html")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
