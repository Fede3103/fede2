import os
import sqlite3
import secrets
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB_PATH = os.environ.get("DATABASE_PATH", "fedekeanu.sqlite3")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Render and similar platforms run behind one trusted reverse proxy.
# Only trust one forwarded address hop; do not read X-Forwarded-For manually.
if os.environ.get("TRUST_PROXY", "0") == "1":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                device_type TEXT,
                operating_system TEXT,
                browser TEXT,
                language TEXT,
                languages TEXT,
                screen_resolution TEXT,
                viewport_size TEXT,
                timezone TEXT,
                protocol TEXT,
                user_agent TEXT,
                ip_address TEXT
            )
        """)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/consent")
def consent():
    if request.form.get("consent") != "yes":
        flash("Per partecipare devi confermare il consenso.")
        return redirect(url_for("index"))

    # These browser details are submitted only after the visitor checks consent.
    fields = {
        "device_type": request.form.get("device_type", "")[:40],
        "operating_system": request.form.get("operating_system", "")[:100],
        "browser": request.form.get("browser", "")[:100],
        "language": request.form.get("language", "")[:40],
        "languages": request.form.get("languages", "")[:200],
        "screen_resolution": request.form.get("screen_resolution", "")[:40],
        "viewport_size": request.form.get("viewport_size", "")[:40],
        "timezone": request.form.get("timezone", "")[:80],
        "protocol": request.form.get("protocol", "")[:20],
        "user_agent": request.headers.get("User-Agent", "unknown")[:500],
    }
    # IP is deliberately stored last in the database/display. It is still personal data.
    ip = (request.remote_addr or "non disponibile")[:100]
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with db() as conn:
        conn.execute("""
            INSERT INTO visits (
                created_at, device_type, operating_system, browser, language,
                languages, screen_resolution, viewport_size, timezone,
                protocol, user_agent, ip_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at, fields["device_type"], fields["operating_system"],
            fields["browser"], fields["language"], fields["languages"],
            fields["screen_resolution"], fields["viewport_size"],
            fields["timezone"], fields["protocol"], fields["user_agent"], ip
        ))
    return render_template("thanks.html")

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not ADMIN_PASSWORD:
            abort(503, "Configura ADMIN_PASSWORD nelle variabili d'ambiente.")
        if secrets.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        flash("Password non corretta.")
    return render_template("login.html")

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin")
@admin_required
def dashboard():
    with db() as conn:
        rows = conn.execute("""
            SELECT id, created_at, device_type, operating_system, browser,
                   language, languages, screen_resolution, viewport_size,
                   timezone, protocol, user_agent, ip_address
            FROM visits ORDER BY id DESC LIMIT 500
        """).fetchall()
        count = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    return render_template("dashboard.html", rows=rows, count=count)

@app.post("/admin/delete")
@admin_required
def delete_data():
    with db() as conn:
        conn.execute("DELETE FROM visits")
    flash("Tutti i dati di test sono stati eliminati.")
    return redirect(url_for("dashboard"))

@app.route("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
