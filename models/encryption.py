import os
import base64
import hashlib
import hmac

from dotenv import load_dotenv
from nacl.secret import SecretBox

load_dotenv()


def get_encryption_key():
    key = os.getenv("SHOPKART_ENCRYPTION_KEY")

    if not key:
        raise RuntimeError(
            "SHOPKART_ENCRYPTION_KEY is missing from .env"
        )

    try:
        key_bytes = base64.urlsafe_b64decode(key.encode())
    except Exception as exc:
        raise RuntimeError(
            "SHOPKART_ENCRYPTION_KEY is invalid"
        ) from exc

    if len(key_bytes) != SecretBox.KEY_SIZE:
        raise RuntimeError(
            "SHOPKART_ENCRYPTION_KEY must decode to 32 bytes"
        )

    return key_bytes


def encrypt_email(email):
    key = get_encryption_key()
    box = SecretBox(key)

    encrypted = box.encrypt(
        email.strip().lower().encode("utf-8")
    )

    return base64.urlsafe_b64encode(encrypted).decode("utf-8")


def decrypt_email(encrypted_email):
    key = get_encryption_key()
    box = SecretBox(key)

    encrypted = base64.urlsafe_b64decode(
        encrypted_email.encode("utf-8")
    )

    decrypted = box.decrypt(encrypted)

    return decrypted.decode("utf-8")
    
    import hashlib
import hmac


def email_lookup(email):
    key = get_encryption_key()

    normalized_email = email.strip().lower().encode("utf-8")

    return hmac.new(
        key,
        normalized_email,
        hashlib.sha256
    ).hexdigest()