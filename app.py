import json
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import Challenge
import crypto

app = FastAPI(title="Secret Match")

# Initialize database tables
init_db()

# Mount static and template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Expiration period for challenges (24 hours)
EXPIRATION_HOURS = 24

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Renders the form to create a new challenge."""
    return templates.TemplateResponse(request, "create.html")

@app.post("/create", response_class=HTMLResponse)
def create_challenge(
    request: Request,
    names: str = Form(...),
    selected_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processes creation of a new secret match challenge."""
    # Parse names split by newline or comma
    raw_list = [n.strip() for n in names.replace(",", "\n").split("\n") if n.strip()]
    
    # Remove duplicates while preserving order
    name_list = []
    for n in raw_list:
        if n not in name_list:
            name_list.append(n)

    if len(name_list) < 2:
        return templates.TemplateResponse(
            request,
            "create.html",
            {
                "error": "Please provide at least 2 distinct names.",
                "names": names,
                "selected_name": selected_name
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if selected_name not in name_list:
        return templates.TemplateResponse(
            request,
            "create.html",
            {
                "error": "Selected name must be one of the listed options.",
                "names": names,
                "selected_name": selected_name
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    token = crypto.generate_secure_token(32)
    salt = crypto.generate_secure_token(16)
    choice_hash = crypto.hash_choice(selected_name, salt)
    
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=EXPIRATION_HOURS)

    challenge = Challenge(
        token=token,
        salt=salt,
        creator_choice_hash=choice_hash,
        names_json=json.dumps(name_list),
        is_used=False,
        created_at=now,
        expires_at=expires_at
    )
    
    db.add(challenge)
    db.commit()

    # Build share link based on current request host
    share_url = str(request.url_for("view_challenge", token=token))

    return templates.TemplateResponse(
        request,
        "created.html",
        {"share_url": share_url}
    )

@app.get("/c/{token}", response_class=HTMLResponse)
def view_challenge(token: str, request: Request, db: Session = Depends(get_db)):
    """Displays the choice options to the second person."""
    challenge = db.query(Challenge).filter(Challenge.token == token).first()

    if not challenge:
        return templates.TemplateResponse(
            request,
            "result.html",
            {"status": "invalid", "message": "Challenge not found or invalid URL."},
            status_code=status.HTTP_404_NOT_FOUND
        )

    now = datetime.now(timezone.utc)
    if challenge.is_used:
        return templates.TemplateResponse(
            request,
            "result.html",
            {"status": "used", "message": "This challenge has already been used and is no longer valid."},
            status_code=status.HTTP_410_GONE
        )

    if challenge.expires_at.tzinfo is None:
        challenge_exp = challenge.expires_at.replace(tzinfo=timezone.utc)
    else:
        challenge_exp = challenge.expires_at

    if now > challenge_exp:
        return templates.TemplateResponse(
            request,
            "result.html",
            {"status": "expired", "message": "This challenge has expired."},
            status_code=status.HTTP_410_GONE
        )

    names = json.loads(challenge.names_json)
    
    return templates.TemplateResponse(
        request,
        "solve.html",
        {"token": token, "names": names}
    )

@app.post("/c/{token}", response_class=HTMLResponse)
def submit_guess(
    token: str,
    request: Request,
    guess: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processes the receiver's choice, enforces single attempt, and returns Match/No match."""
    challenge = db.query(Challenge).filter(Challenge.token == token).first()

    if not challenge:
        return templates.TemplateResponse(
            request,
            "result.html",
            {"status": "invalid", "message": "Challenge not found."},
            status_code=status.HTTP_404_NOT_FOUND
        )

    now = datetime.now(timezone.utc)
    if challenge.expires_at.tzinfo is None:
        challenge_exp = challenge.expires_at.replace(tzinfo=timezone.utc)
    else:
        challenge_exp = challenge.expires_at

    # Strictly enforce one-time usage and expiry
    if challenge.is_used or now > challenge_exp:
        return templates.TemplateResponse(
            request,
            "result.html",
            {"status": "invalid", "message": "This challenge is no longer active or has already been completed."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Invalidate immediately to prevent race conditions or secondary submissions
    challenge.is_used = True
    db.commit()

    # Compare hashes
    guest_hash = crypto.hash_choice(guess, challenge.salt)
    is_match = (guest_hash == challenge.creator_choice_hash)

    result_text = "Match" if is_match else "No match"
    
    return templates.TemplateResponse(
        request,
        "result.html",
        {"status": "success", "result": result_text}
    )