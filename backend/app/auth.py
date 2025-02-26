from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, Cookie
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import Response, RedirectResponse
from dotenv import load_dotenv
import httpx
import os
import jwt
import secrets
from typing import Any
from datetime import datetime, timedelta, timezone
import mysql


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
    from .main import get_gmail
    if session_id is None or not get_session(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated session_id: {get_session(session_id)}",
        )
    else:
        user_id = get_session(session_id)[1]
        user = get_gmail(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cloud not validate credentials",
            )
        return user


#############################################################
router = APIRouter()

# 環境変数の読み込み
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

ACCESS_TOKEN_EXPIRE_MINUTES = 10
SESSION_ID_LENGTH = 32


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL
)

#############################################################
# データベース関係
# セッションの取得
def get_session(session_id: str):
    from .main import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM user_auth WHERE user_auth_id = (%s)"
        cursor.execute(query, (session_id,))
        session = cursor.fetchone()
        if session is None:
            return
        else:
            return session
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error gettin session: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# セッションの追加
def add_session(session_id: str, user_id: int):
    from .main import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO user_auth (user_auth_id, user_id, date) VALUES (%s, %s, %s)"
        expires_at = (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (session_id, user_id, expires_at))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error adding session: {err}")
    finally:
        cursor.close()
        conn.close()

#############################################################
# ルート

# ログイン
@router.get("/login")
async def login():
    auth_url = (
        f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&"
        f"access_type=offline&prompt=consent"
    )
    return {"auth_url": auth_url}

# ログイン後に呼び出されるコールバック
@router.get("/login/callback/")
async def login_callback(code: str = Query(...)):
    redirect_url = "http://localhost:3000/TopPage"

    from .main import get_user_id, insert_gmail
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
    gmail = decode_email(token_response_json["id_token"])

    user_id = get_user_id(gmail)

    if user_id == -1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    elif user_id is None:
        insert_gmail(gmail)
        user_id = get_user_id(gmail)[0]
        redirect_url = "http://localhost:3000/WelcomePage"
    else:
        user_id = user_id[0]

    session_id = create_session_id()
    add_session(session_id, user_id)

    response = RedirectResponse(url=redirect_url)

    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    response.set_cookie(
        key="session_id",
        value=session_id,
        expires=expires,
        httponly=True,
    )

    return response

@router.get("/authtest")
async def test(current_user: Any = Depends(get_current_user)):
    return {"user": current_user}