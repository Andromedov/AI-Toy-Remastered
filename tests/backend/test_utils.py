from backend.utils import hash_password, check_password, generate_token

def test_hash_and_check_password():
    raw = "mysecurepassword"
    hashed = hash_password(raw)
    assert hashed != raw
    assert check_password(raw, hashed)

def test_generate_token():
    token = generate_token("user@example.com")
    assert isinstance(token, str)
    assert len(token) > 20