import secrets
import hashlib


def generar_token():
    return secrets.token_urlsafe(32)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def sanitize_filename(name):
    import re
    name = str(name)
    name = re.sub(r"[^\w\s\-\.]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:200]
