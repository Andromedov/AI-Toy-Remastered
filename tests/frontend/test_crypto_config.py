import json
from frontend.login_view import get_fernet

def test_encryption_cycle():
    fernet = get_fernet()
    plain = "sk-key"
    encrypted = fernet.encrypt(plain.encode()).decode()
    decrypted = fernet.decrypt(encrypted.encode()).decode()
    assert decrypted == plain

def test_config_write_and_read(tmp_path):
    config_file = tmp_path / "config.json"
    fernet = get_fernet()

    data = {
        "email": "user@example.com",
        "jwt_token": "token123",
        "api_key": fernet.encrypt(b"sk-test").decode()
    }
    with open(config_file, "w") as f:
        json.dump(data, f)

    with open(config_file) as f:
        loaded = json.load(f)
    assert fernet.decrypt(loaded["api_key"].encode()).decode() == "sk-test"