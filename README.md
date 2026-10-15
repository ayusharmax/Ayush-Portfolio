# Ayush Sharma — Full-stack Portfolio

This project includes:
- Responsive portfolio frontend (`static/index.html`)
- FastAPI backend (`main.py`)
- SQLite database created automatically at first run
- Working contact form that saves messages to SQLite
- Public projects API
- Optional admin API to list contact messages and add projects, protected by an API key

## 1. Requirements
- Python 3.10 or newer

## 2. Run locally

Open a terminal in this folder and run:

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install packages and start the server:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

API health check: `http://127.0.0.1:8000/api/health`
Interactive API docs: `http://127.0.0.1:8000/docs`

The database file `portfolio.db` is created automatically when the server starts.

## 3. Admin endpoints (optional)

The admin endpoints are disabled until you set an API key. Use a long, private key and never publish it in frontend code or commit it to GitHub.

**macOS/Linux**
```bash
export ADMIN_API_KEY="replace-with-a-long-random-secret"
uvicorn main:app --reload
```

**Windows PowerShell**
```powershell
$env:ADMIN_API_KEY="replace-with-a-long-random-secret"
uvicorn main:app --reload
```

Then send the key in the `X-Admin-Key` header:
- `GET /api/admin/messages` — read saved contact messages
- `POST /api/admin/projects` — add a project
- `DELETE /api/admin/messages/{message_id}` — delete a message

Example JSON for `POST /api/admin/projects`:
```json
{
  "title": "My first project",
  "description": "A short description of the project.",
  "tech_stack": "Python, FastAPI",
  "project_url": "https://example.com"
}
```

## Important before deploying
- This project has not been deployed online yet.
- Set a strong `ADMIN_API_KEY` using your hosting provider's secret/environment settings.
- Make sure the host provides persistent storage for `portfolio.db`; some free hosting filesystems reset on redeploy/restart. For production, consider a managed database.
- Add real social links and personal details before publishing.
- The contact form saves messages in the database; it does not automatically email you. Email notifications need an email provider and configuration.
- Add rate limiting / spam protection before sharing the form widely.
