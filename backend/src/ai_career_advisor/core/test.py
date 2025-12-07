from ai_career_advisor.core.jwt_handler import create_access_token, decode_access_token

token = create_access_token({"user_id": 10})
print("JWT:", token)

payload = decode_access_token(token)
print("Decoded:", payload)
