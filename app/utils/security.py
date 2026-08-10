import secrets
from werkzeug.security import generate_password_hash, check_password_hash


def generar_token():
    return secrets.token_urlsafe(32)


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed):
    return check_password_hash(hashed, password)


def sanitize_filename(name):
    import re
    name = str(name)
    name = re.sub(r"[^\w\s\-\.]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:200]
