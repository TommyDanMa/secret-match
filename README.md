# Secret Match Web Application

A zero-knowledge match verification service built with FastAPI, SQLite, and Jinja2 templates.

---

## Step-by-Step Deployment Guide

Follow these simple steps to get your app running live on Render for free without any prior web development experience.

---

### Step 1: Install Python & Git

1. **Python**: Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/). Ensure you check the box that says **"Add Python to PATH"** during installation.
2. **Git**: Download and install Git from [git-scm.com](https://git-scm.com/downloads).

---

### Step 2: Prepare the Project Locally

1. Create a directory named `secret-match` on your computer.
2. Place all the project files (`app.py`, `database.py`, `models.py`, `crypto.py`, `requirements.txt`, `render.yaml`, `Procfile`, `templates/`, `static/`) inside that directory.
3. Open a terminal or Command Prompt in your `secret-match` directory and test running locally:
   ```bash
   pip install -r requirements.txt
   uvicorn app:app --reload