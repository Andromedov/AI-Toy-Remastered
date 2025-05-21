from backend.utils import is_valid_email, is_valid_username

def test_valid_email():
    assert is_valid_email("test@example.com")
    assert not is_valid_email("invalid-email")

def test_valid_username():
    assert is_valid_username("username_123")
    assert not is_valid_username("x")
    assert not is_valid_username("this_is_way_too_long_for_a_username")