from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, Cookie
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import Response, RedirectResponse, JSONResponse
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
    while True:
        session_id = secrets.token_hex(SESSION_ID_LENGTH)
        if not get_session(session_id):
            return session_id

# セッションを用いた検証
async def get_current_user(session_id: str = Cookie(None)):
    from .main import get_gmail
    # print(f'ブラウザのsessionid: {session_id}')
    if session_id is None or not get_session(session_id):
        # print('ブラウザのセッションとデータベースのセッションが違った')
        return False
    else:
        user_id = get_session(session_id)[2]
        # print(f'user_id: {user_id}')
        user = get_gmail(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cloud not validate credentials",
            )
        return user

# ログインページリダイレクト専用関数
def to_login():
    return RedirectResponse(url="http://localhost:3000")


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
    print(f'ブラウザのsessionid: {session_id}')
    from .main import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM user_auth WHERE user_auth_id = (%s)"
        cursor.execute(query, (session_id,))
        session = cursor.fetchone()
        if session is None:
            print('データベースにuser_auth_idがありませんでした。')
            return
        else:
            return session
    except mysql.connector.Error as err:
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

# アンケートに答えたかどうかの判別
def answerd_survey(user_id: int):
    from .main import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM survey WHERE userid = (%s)"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        print("リザルト")
        print(result)
        if result is None:
            return False
        else:
            return True
    except mysql.connector.Error as err:
        print(f"Error getting user from surcey: {err}")
        return None
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

# ログアウト
@router.get("/logout")
async def logout(response: Response):
    print("ログアウト処理が呼び出されました")
    response = RedirectResponse(url="http://localhost:3000")
    response.delete_cookie("session_id")
    return response

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
    # トークンからgmailをデコード
    gmail = decode_email(token_response_json["id_token"])

    # accountテーブルに gmail が存在するか確認
    account_record = get_user_id(gmail)
    if account_record is None:
        # 存在しなければ新規登録
        inserted_id = insert_gmail(gmail)
        if inserted_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register account"
            )
        # 登録後に再取得
        account_record = get_user_id(gmail)
        if account_record is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve account information"
            )
    # get_user_id() の戻り値はタプルで返っていると仮定（例: (user_id, )）
    user_id = account_record[0]

    # セッションIDの生成と user_auth への登録
    session_id = create_session_id()
    add_session(session_id, user_id)

    # アンケート回答済みかどうかでリダイレクト先を分岐
    if not answerd_survey(user_id):
        redirect_url = "http://localhost:3000/QuestionPage"

    response = RedirectResponse(url=redirect_url)

    # クッキーにセッションIDを設定（有効期限はACCESS_TOKEN_EXPIRE_MINUTES分）
    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    response.set_cookie(
        key="session_id",
        value=session_id,
        expires=expires,
        httponly=True,
    )

    return response

#　テスト用のルート
@router.get("/authtest")
async def test(current_user: Any = Depends(get_current_user)):
    if not current_user:
        return to_login()
    return {"user": current_user}