from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.schema import SystemMessage, HumanMessage, Document
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, EmailStr
import mysql.connector
import datetime
import json
import os
from . import auth
import faiss
from openai import OpenAI
import openai
from dotenv import load_dotenv
import numpy as np
from typing import Any
# from .auth import get_current_user, to_login, get_session

#############################################################
# 初期設定
app = FastAPI()

router = APIRouter()

app.include_router(auth.router)

app_env = os.getenv("FASTAPI_ENV", "development")
if app_env == "development":
    allow_credentials = True
    origins = ["http://localhost:3000"]
else:
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

load_dotenv()
# 変数を取得
key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(
    api_key=key
)

llm = ChatOpenAI(
    model_name="gpt-4o-mini-2024-07-18",
    temperature=0,
    openai_api_key=key
)

#############################################################
# データベース関係

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="db",  # docker-composeの場合、MySQLコンテナのサービス名
            user="user",
            password="password",
            database="db",
            use_unicode = True,
            charset="utf8mb4"
        )
        return conn
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")

# user_id取得
def get_user_id(gmail: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id FROM account WHERE gmail = (%s)"
        cursor.execute(query, (gmail,))
        user_id = cursor.fetchone()
        return user_id
    except mysql.connector.Error as err:
        print(f"Error getting user_id: {err}")
        return -1
    finally:
        cursor.close()
        conn.close()

# gmail取得
def get_gmail(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id, gmail FROM account WHERE id = (%s)"
        cursor.execute(query, (user_id,))
        account = cursor.fetchone()
        return account
    except mysql.connector.Error as err:
        print(f"Error getting gmail: {err}")
        return -1
    finally:
        cursor.close()
        conn.close()

# gmail挿入
def insert_gmail(gmail: str):
    # データベース接続の取得
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # パラメータ化されたクエリで安全にINSERT処理
        query = "INSERT INTO account (gmail) VALUES (%s)"
        cursor.execute(query, (gmail,))
        conn.commit()
        inserted_id = cursor.lastrowid
        print(f"Inserted record with ID: {inserted_id}")
        return inserted_id
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error inserting gmail: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# ログ挿入
def insert_read_log(user_id: int, article_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO read_log (user_id, article_id) VALUES (%s, %s)"
        cursor.execute(query, (user_id, article_id))
        conn.commit()
        inserted_id = cursor.lastrowid
        print(f"Inserted read_log with ID: {inserted_id}")
        return inserted_id
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error inserting read_log: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

class BlogPostSchema(BaseModel):
    id: int
    title: str
    summary150: str
    summary1000: str
    content: str
    url: str
    published_date: str  # 日付は文字列として扱います
    created_at: str

# /TopPage は固定ダミーデータを返す
class TopPageItem(BaseModel):
    id: int
    title: str
    summary50: str
    summary1000: str
    content: str
    url: str
    published_date: str
    created_at: str

# アカウント登録用のPydanticモデル
class AccountIn(BaseModel):
    gmail: EmailStr

# ログ登録用のモデル
class ReadLogIn(BaseModel):
    user_id: int
    article_id: int

# Pydanticモデル（出力用）
class RecommendArticle(BaseModel):
    id: int
    title: str
    summary150: str
    summary1000: str
    content: str
    url: str
    published_date: str
    created_at: str

# お気に入りのサイト登録用  
class FavoriteSiteIn(BaseModel):
    url: str

# アンケート入力用のPydanticモデル
class SurveyIn(BaseModel):
    userid: int
    age: int
    # gender は '男', '女', 'その他' のいずれかであることを前提
    gender: str  
    job: str
    preferred_article_detail: str

#############################################################

# ユーザーごとにレコメンドするエンドポイント
def read_articles():
    """
    DBから記事情報を取得して、各行の日時をISO形式に変換し、リスト(dict)で返す
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title, summary150, summary1000, content, url, published_date, created_at "
            "FROM article ORDER BY published_date DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")
    
    for row in rows:
        if isinstance(row.get("created_at"), (datetime.date, datetime.datetime)):
            row["created_at"] = row["created_at"].isoformat()
        if isinstance(row.get("published_date"), (datetime.date, datetime.datetime)):
            row["published_date"] = row["published_date"].isoformat()
    return rows

def get_embedding(text, model="text-embedding-ada-002"):
    """
    OpenAI APIを使って、テキストの埋め込みベクトルを取得
    """
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    # response.data はリスト。最初のembeddingを返す
    return response.data[0].embedding

def get_combined_embedding(keywords):
    """
    与えられた複数のキーワードの埋め込みを取得し、平均化して一つの埋め込みベクトルを作成する
    """
    embeddings = [get_embedding(keyword) for keyword in keywords]
    combined_embedding = np.mean(embeddings, axis=0)  # 平均をとる
    return combined_embedding.astype('float32')

def search_articles(query_text, k=10):
    """
    query_textから埋め込みを生成し、FAISSインデックスから上位 k 件を返す
    """
    query_embedding = get_embedding(query_text)
    query_np = np.array([query_embedding]).astype('float32')
    # FAISSインデックスのファイルパス（事前に構築済みのものを読み込む）
    index = faiss.read_index("/app/app/index_data/faiss_index.faiss")
    distances, indices = index.search(query_np, k)
    return distances[0], indices[0]

#############################################################
# ルート

# 記事全取得テスト
@app.get("/test", response_model=list[BlogPostSchema])
def test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title, summary150, summary1000, content, url, published_date, created_at "
            "FROM article ORDER BY published_date DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print(rows)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")

    # 日付や日時オブジェクトがある場合、ISO形式に変換
    for row in rows:
        if isinstance(row.get("created_at"), (datetime.date, datetime.datetime)):
            row["created_at"] = row["created_at"].isoformat()
        if isinstance(row.get("published_date"), (datetime.date, datetime.datetime)):
            row["published_date"] = row["published_date"].isoformat()

    return JSONResponse(content=rows, media_type="application/json; charset=utf-8")

# アカウント登録エンドポイント（POSTリクエスト）
@app.post("/register_account")
def register_account(account: AccountIn):
    inserted_id = insert_gmail(account.gmail)
    if inserted_id is None:
        raise HTTPException(status_code=400, detail="Failed to insert account")
    return JSONResponse(
        content={"message": "Account registered successfully", "id": inserted_id},
        media_type="application/json; charset=utf-8"
    )

# /recommend エンドポイント
@app.get("/recommend", response_model=list[RecommendArticle])
def recommend():
    user_id = 1  # 仮定のユーザーID。実際は認証情報等から取得
    
    # survey テーブルからユーザーの好みを取得する関数
    def get_user_preference(user_id: int) -> str:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT preferred_article_detail FROM survey WHERE userid = %s"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row and row.get("preferred_article_detail"):
                return row["preferred_article_detail"]
            else:
                raise HTTPException(status_code=404, detail="User survey data not found")
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database query error: {err}")

    # surveyテーブルから好みを取得
    preferred_article_detail = get_user_preference(user_id)
    print("ユーザーの好み:", preferred_article_detail)
    
    # LLMに好みからジャンルキーワードのみ抽出させる
    messages = [
        SystemMessage(content="あなたは、ユーザーの好みの文章から関連するジャンルキーワードを抽出するアシスタントです。"),
        HumanMessage(content=f"{preferred_article_detail}に関連するジャンルの単語のみを出力して。")
    ]
    llm_response = llm(messages)  # ここでLLMが応答
    genre_keywords = llm_response.content.strip()  # 例: "技術, AI, IoT"
    print("抽出されたジャンルキーワード:", genre_keywords)
    print(type(genre_keywords))
    
    # FAISSで類似検索（上位10件）
    distances, indices = search_articles(genre_keywords, k=10)
    
    # DBから全記事を取得
    articles = read_articles()
    
    # FAISSのインデックスは記事リストのインデックスに対応していると仮定
    recommended = []
    for idx in indices:
        if idx < len(articles):
            recommended.append(articles[idx])
    
    print(f"推奨記事件数: {len(recommended)}")
    return JSONResponse(content=recommended, media_type="application/json; charset=utf-8")

# フロント開発用にダミーデータを返す関数
@app.get("/TopPage", response_model=list[TopPageItem])
def top_page(current_user: Any = Depends(auth.get_current_user)):
    print(f'current_user: {current_user}')
    if not current_user:
        print("ユーザーの取得に失敗しました")
        raise HTTPException(status_code=401, detail="Not authenticated")
    dummy_data = [
        {
            "id": 0,
            "title": "最新ニュース: テクノロジーの革新",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "本日のニュースでは、最新のテクノロジートレンドに関する詳細な分析をお届けします。"
                "AI、IoT、そしてブロックチェーン技術の急速な発展により、今後の産業構造が大きく変化することが期待されます。"
            ),
            "content": (
                "詳細記事: 新技術の導入事例、専門家のインタビュー、及び市場分析を通じて、"
                "今後の展望について考察します。"
            ),
            "url": "https://example.com/news/tech",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T14:19:38.266Z"
        },
        {
            "id": 1,
            "title": "経済ニュース: 市場動向レポート",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "本日の経済ニュースは、国内外の市場動向に焦点を当てたレポートです。"
                "主要株価指数の急変や、最新の経済指標、そして政府の経済政策に関する情報を詳細に分析しています。"
            ),
            "content": (
                "記事内容: 市場における最新のデータと、専門家による分析を基に、"
                "今後の投資戦略やリスクについて解説します。"
            ),
            "url": "https://example.com/news/economy",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T14:19:38.266Z"
        },
        {
            "id": 2,
            "title": "エンタメ: 映画レビュー特集",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "エンターテインメント分野では、最新公開の映画に関するレビューが注目を集めています。"
                "ストーリー、演技、映像美、そして音楽のクオリティに至るまで、総合的な評価を行いました。"
            ),
            "content": (
                "レビュー記事: 最新の話題作について、監督やキャストのコメント、映画の見どころを徹底分析します。"
            ),
            "url": "https://example.com/news/entertainment",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T14:19:38.266Z"
        },
        {
            "id": 3,
            "title": "スポーツ: 国際大会速報",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "スポーツニュースでは、国際大会での注目試合について速報をお伝えします。"
                "各国のエース選手が激突する中、戦術やパフォーマンスに注目が集まっています。"
            ),
            "content": (
                "詳細記事: 試合のハイライト、選手インタビュー、戦術解析など、熱い戦いの全貌をレポートします。"
            ),
            "url": "https://example.com/news/sports",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T15:00:00.000Z"
        },
        {
            "id": 4,
            "title": "政治: 政策発表と議論",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "政治の最新動向として、政府が重要な政策を発表し、議会で活発な議論が交わされています。"
                "政策の影響や今後の見通しについて、専門家の意見も取り入れた詳細な分析をお届けします。"
            ),
            "content": (
                "詳細記事: 政策の背景、国会での議論、各方面からの反応など、政治の最前線を伝えます。"
            ),
            "url": "https://example.com/news/politics",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T15:15:00.000Z"
        },
        {
            "id": 5,
            "title": "健康: 新しいライフスタイル提案",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "健康ニュースでは、最新のライフスタイル提案や健康法、栄養情報を紹介。"
                "ストレス管理や運動、食事法に関する専門家のアドバイスが豊富です。"
            ),
            "content": (
                "詳細記事: 日常生活に取り入れられる健康法、最新の栄養トレンド、運動プログラムなど、健康維持のための情報を提供します。"
            ),
            "url": "https://example.com/news/health",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T15:30:00.000Z"
        },
        {
            "id": 6,
            "title": "ビジネス: 企業戦略の転換",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "ビジネスニュースでは、業界の注目企業が新たな戦略を発表し、市場でのポジションを再定義する動きについて解説します。"
                "競合分析や今後の見通しにも迫ります。"
            ),
            "content": (
                "詳細記事: 企業インタビュー、業界専門家のコメント、戦略転換の背景や影響を詳しくレポートします。"
            ),
            "url": "https://example.com/news/business",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T15:45:00.000Z"
        },
        {
            "id": 7,
            "title": "国際: 世界情勢の変化",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "国際ニュースでは、各国間の外交関係や国際会議の結果など、世界情勢における重要な変化を詳しく伝えます。"
                "地域ごとの影響や今後の課題についても分析します。"
            ),
            "content": (
                "詳細記事: 各国代表者の発言、国際的な反応、影響分析など、グローバルな視点から報道します。"
            ),
            "url": "https://example.com/news/international",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T16:00:00.000Z"
        },
        {
            "id": 8,
            "title": "ライフスタイル: 新しい暮らしの提案",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "ライフスタイルニュースでは、日常生活を豊かにする新しいアイディアやトレンド、インテリアやDIYの情報を紹介します。"
                "生活の質を向上させるためのヒントが満載です。"
            ),
            "content": (
                "詳細記事: トレンド紹介、専門家のアドバイス、実際の事例を元に、新しい暮らし方を提案します。"
            ),
            "url": "https://example.com/news/lifestyle",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T16:15:00.000Z"
        },
        {
            "id": 9,
            "title": "カルチャー: 芸術と文化の探求",
            "summary50": "新たな技術が市場に衝撃を与えるあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ",
            "summary1000": (
                "カルチャーニュースでは、現代アートや音楽、伝統文化に焦点を当て、"
                "世界各地の文化的イベントや展覧会の情報をお届けします。"
            ),
            "content": (
                "詳細記事: 芸術家のインタビュー、イベントレポート、文化の背景にあるストーリーなど、"
                "多角的な視点から文化を探求します。"
            ),
            "url": "https://example.com/news/culture",
            "published_date": "2025-02-23",
            "created_at": "2025-02-23T16:30:00.000Z"
        }
    ]
    return JSONResponse(content=dummy_data, media_type="application/json; charset=utf-8")

# 既読エンドポンイト
@app.post("/log_read")
def log_read_event(log: ReadLogIn, current_user: Any = Depends(auth.get_current_user)):
    inserted_id = insert_read_log(log.user_id, log.article_id)
    if inserted_id is None:
        raise HTTPException(status_code=401, detail="Failed to insert read log")
    return JSONResponse(
        content={"message": "Read log recorded", "id": inserted_id},
        media_type="application/json; charset=utf-8"
    )

# 興味のあるサイトをsource_urlテーブルに保存するエンドポイント
@router.post("/regist_favorite_site")
def regist_favorite_site_event(favorite: FavoriteSiteIn, current_user: Any = Depends(auth.get_current_user)):
    if not current_user:
        print("ユーザーの取得に失敗しました")
        raise HTTPException(status_code=401, detail="Not authenticated")
    # current_userからユーザーIDを取得（get_gmailの戻り値に合わせる）
    user_id = current_user[0]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # まず、source_url テーブルに同じURLが存在するかチェック
        select_query = "SELECT id FROM source_url WHERE url = %s"
        cursor.execute(select_query, (favorite.url,))
        result = cursor.fetchone()
        if result:
            source_id = result[0]
        else:
            # 存在しなければ、新規登録
            insert_source = "INSERT INTO source_url (url) VALUES (%s)"
            cursor.execute(insert_source, (favorite.url,))
            conn.commit()
            source_id = cursor.lastrowid

        # 次に、favorite_sites テーブルに登録（ユーザーとsource_id の組み合わせ）
        insert_favorite = "INSERT INTO favorite_sites (user_id, source_id) VALUES (%s, %s)"
        cursor.execute(insert_favorite, (user_id, source_id))
        conn.commit()
        favorite_id = cursor.lastrowid

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

    return JSONResponse(
        content={"message": "Favorite site registered", "favorite_id": favorite_id},
        media_type="application/json; charset=utf-8"
    )

# アンケート登録エンドポイント
@app.post("/regist_survey")
def regist_survey(
    survey: SurveyIn, 
    current_user: Any = Depends(auth.get_current_user)
):
    if not current_user:
        print("ユーザーの取得に失敗しました")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # current_user は例えば (user_id, gmail) などのタプルとして取得されると仮定
    user_id = current_user[0]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = (
            "INSERT INTO survey (userid, age, gender, job, preferred_article_detail) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        # クライアントから送信された userid は無視し、current_user の値を使用
        values = (user_id, survey.age, survey.gender, survey.job, survey.preferred_article_detail)
        cursor.execute(query, values)
        conn.commit()
        inserted_id = cursor.lastrowid
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database insert error: {err}")
    finally:
        cursor.close()
        conn.close()
    return JSONResponse(
        content={"message": "Survey data registered", "id": inserted_id},
        media_type="application/json; charset=utf-8"
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)