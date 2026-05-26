from src.auth.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    hashed = hash_password("Senha@123")
    assert verify_password("Senha@123", hashed)
    assert not verify_password("Errada", hashed)


def test_token_roundtrip():
    token = create_access_token({"user_id": 1, "perfil": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == 1
