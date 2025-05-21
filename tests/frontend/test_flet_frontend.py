import pytest
from unittest.mock import patch, MagicMock
from frontend.main import handle_send_message, load_api_key

@patch("frontend.main.requests.post")
def test_handle_send_message_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "Hello!"}

    mock_text_field = MagicMock()
    mock_text_field.value = "Hi"

    mock_chat = MagicMock()
    mock_api_key = "test_key"

    result = handle_send_message(mock_text_field, mock_chat, mock_api_key)

    mock_post.assert_called_once()
    assert result == "Hello!"

def test_load_api_key(tmp_path):
    test_file = tmp_path / "api_key.txt"
    test_file.write_text("test-key-123")

    with patch("frontend.main.API_KEY_FILE", str(test_file)):
        key = load_api_key()
        assert key == "test-key-123"