import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    raw_pass = "segredo123"
    hashed = get_password_hash(raw_pass)
    
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("senha_errada", hashed) is False

def test_jwt_token_lifecycle():
    user_id = 42
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    
    assert payload is not None
    assert payload["sub"] == "42"
