from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, Cookie
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import httpx
import os
import jwt
import secrets


#############################################################
# 関数群

# JWTをデコードしてemailを返す
def decode_email(tokenid):
    decode_payload = jwt.decode(tokenid, options={"verify_signature": False})
    return decode_payload.get("email")

# セッションIDの生成
def create_session_id() -> str:
    session_id = secrets.token_hex(SESSION_ID_LENGTH)
    return session_id

# セッションを用いた検証
async def get_current_user(session_id: str = Cookie(None)):

#############################################################
router = APIRouter()

# 環境変数の読み込み
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SESSION_ID_LENGTH = 32


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL
)

#############################################################
# ルート
@router.get("/login")
async def login():
    auth_url = (
        f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&"
        f"access_type=offline&prompt=consent"
    )
    return {"auth_url": auth_url}

@router.get("/login/callback/")
async def login_callback(code: str = Query(...)):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
    token_response_json = token_response.json()
    try:
        token_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json()
        )
    return decode_email(token_response_json["id_token"])