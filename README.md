# Secret Match

A small **FastAPI**, **SQLite**, and **Jinja2** application that lets two people
compare a selection from a shared list. The other participant sees “Match” or
“No match”; the server receives both submitted choices.

## Privacy and security limits

This is **not a formal zero-knowledge protocol**, private set intersection, or
end-to-end encrypted matching. The server is trusted. It receives the creator's
choice and the receiver's guess in plaintext request fields. It stores the full
candidate list, a random salt, and SHA-256(salt + ":" + normalized choice), rather
than storing a separate plaintext creator-choice column. The chosen name is still
present among the stored candidates. Anyone with database access can enumerate
that small list against the hash and infer the choice. Salting does not prevent
this attack. Server operators, logging middleware, or compromised hosting may
observe requests. A match reveals the common selection to the receiver.

A challenge URL is a bearer link: anyone holding it can see the list and consume
the attempt. One valid submission consumes it even if the guess is wrong. A single
conditional database update claims an unused, unexpired challenge, so only one
concurrent submission can return a result. Links expire after 24 hours; rows are
not automatically deleted. There is no account authentication, rate limiting, or
comprehensive production security audit. Repeated newly created challenges and
information outside the app can still reveal choices. Use fictional data for demos;
do not use this prototype for sensitive personal information.

## Local setup

Use Python 3.11+ and run commands from the repository root:

```bash
git clone https://github.com/TommyDanMa/secret-match.git
cd secret-match
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

On Windows, activate with `.venv\Scripts\activate`. Open
[the local application](http://127.0.0.1:8000/). SQLite creates `app.db` in the
working directory. Keep that database and any `.env` files out of version control.
Deployment requires Python dependencies and writable, persistent storage for SQLite;
it does not have zero dependencies. Free hosting can sleep or lose ephemeral data.
Use HTTPS for any hosted instance.

## Fictional demonstration and regression checks

1. Enter `Alice`, `Bob`, and `Charlie` as fictional candidates and select `Alice`.
2. Open the generated link and choose `Alice`: the result is “Match”.
3. Submit that link again: it is rejected as already completed.
4. Create another challenge and guess `Bob`: “No match”, with no retry.

```bash
python -m pip install pytest httpx
python -m pytest -q
```

The tests use a temporary SQLite database and fictional candidates. They exercise
matching, mismatching, replay rejection, expiry, validation, and concurrent requests.
A passing run supports these tested cases, not a universal privacy guarantee.

## Contributions and AI assistance

Tommy identified the practical need and specified the requested functionality,
including single-use challenge links and expiration.
Most of the original implementation was AI-generated; manually writing code was
not the main objective. The exact original AI tool and file-level division of work
are not recorded here. Codex produced the November 2026 conditional-update fix,
regression tests, and documentation corrections. FastAPI, SQLAlchemy, Jinja2,
Uvicorn, python-multipart and Pydantic provide external dependencies; Python's
`hashlib` and `secrets` implement hashing and token generation. See `requirements.txt`
and the source imports. No claim of original cryptographic research is made.
