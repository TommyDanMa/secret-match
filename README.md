# Secret Match

A privacy-focused, zero-knowledge match verification web application built with **FastAPI**, **SQLite**, and **Jinja2**. 

Secret Match allows two people to check whether they selected the same person from a custom list without ever exposing or storing the chosen name in plain text, unless both users select the same candidate.

---

## Features

* **Zero-Knowledge Verification:** Names are never stored in plain text or simple, easy-to-guess hashes. The app uses unique per-challenge secret salts with SHA-256 digests.
* **Single-Use Links:** Every challenge URL can only be attempted **once**. After one submission, the challenge is permanently deactivated to prevent brute-force or guessing attacks.
* **Expiration Enforcement:** Links automatically expire after a configurable timeframe (default: 24 hours).
* **Cryptographically Secure Tokens:** Challenge URLs use high-entropy random tokens that cannot be guessed or enumerated.
* **No Client-Side Reliance:** All security checks, hash comparisons, and one-time constraints are strictly enforced on the server.
* **Zero Dependencies for Deployment:** Runs easily on free hosting tiers like Render using SQLite.

---

## Tech Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn
* **Database:** SQLite, SQLAlchemy ORM
* **Frontend:** Jinja2 HTML Templates, Custom CSS
* **Security:** Python `hashlib` (SHA-256) & `secrets` module

---

## Quick Start (Local Development)

### 1. Prerequisites
Ensure you have **Python 3.11+** installed on your system.

### 2. Setup & Installation

Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/YOUR_USERNAME/secret-match.git](https://github.com/YOUR_USERNAME/secret-match.git)
cd secret-match
```
Create and activate a virtual environment (optional, but recommended):
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```
Install the required dependencies:
```bash
pip install -r requirements.txt
```
### 3. Run the Application
Start the development server using
```bash
Uvicorn:Bashuvicorn app:app --reload
```
Open your browser and navigate to http://127.0.0.1:8000.


## Security & Privacy Overview

- **Salting & Hashing:** Because candidate lists are typically small (e.g., 8 names), simple hashes are vulnerable to local lookup attacks. To solve this, the server generates a unique cryptographic salt for every created challenge:

  ```math
  Hash = SHA256(Salt ∥ Normalized_Name)
  ```
- **Race-Condition Safe:** The database marks a challenge as is_used = True before evaluating the match result, completely locking out concurrent or repeated attempts.
- **No Target Leakage:** The second user is shown only "Match" or "No match" upon submission, preventing any information leakage beyond the direct match result.
