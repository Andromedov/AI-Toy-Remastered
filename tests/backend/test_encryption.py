import pytest
from backend.encryption import encrypt_api_key, decrypt_api_key

def test_encrypt_decrypt_cycle():
    key = "secret-key-123"
    encrypted = encrypt_api_key(key)
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == key