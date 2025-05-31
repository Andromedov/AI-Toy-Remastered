import json
from frontend.login_view import get_fernet

def test_fernet_encryption_cycle():
    fernet = get_fernet()
    original = "test-key"
    encrypted = fernet.encrypt(original.encode()).decode()
    decrypted = fernet.decrypt(encrypted.encode()).decode()
    assert decrypted == original

def test_config_read_write(tmp_path):
    config_file = tmp_path / ".config.json"
    fernet = get_fernet()

    encrypted_key = fernet.encrypt(b"sk-test").decode()
    with open(config_file, "w") as f:
        json.dump({
            "email": "user@example.com",
            "jwt_token": "token123",
            "api_key": encrypted_key
        }, f)

    with open(config_file) as f:
        data = json.load(f)
        assert fernet.decrypt(data["api_key"].encode()).decode() == "sk-test"