import secrets
import hashlib

def generate_secure_token(length: int = 32) -> str:
    """Generates a cryptographically secure random URL token."""
    return secrets.token_urlsafe(length)

def hash_choice(choice: str, salt: str) -> str:
    """
    Hashes a choice with a per-challenge salt using SHA-256.
    Normalizes input string by stripping whitespace and converting to lowercase.
    """
    normalized = choice.strip().lower()
    salted = f"{salt}:{normalized}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()