from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import datetime
import json
import os

app = FastAPI()

app_env = os.getenv("FASTAPI_ENV", "development")
if app_env == "development":
    allow_credentials = False
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

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="db",  # docker-composeの場合、MySQLコンテナのサービス名
            user="user",
            password="password",
            database="db",
            charset="utf8mb4"
        )
        return conn
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")

class BlogPostSchema(BaseModel):
    id: int
    title: str
    summary150: str
    summary1000: str
    content: str
    url: str
    published_date: str  # 日付は文字列として扱います
    created_at: str

@app.get("/test", response_model=list[BlogPostSchema])
def read_articles():
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

@app.get("/TopPage", response_model=list[TopPageItem])
def top_page():
    dummy_data = [
        {
            "id": 0,
            "title": "最新ニュース: テクノロジーの革新",
            "summary50": "新たな技術が市場に衝撃を与える。",
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
            "summary50": "株式市場に変動、注目の経済指標も。",
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
            "summary50": "今話題の最新映画を徹底レビュー。",
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
        }
    ]
    return JSONResponse(content=dummy_data, media_type="application/json; charset=utf-8")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)

# from fastapi import FastAPI, Depends, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, Response
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date
# from sqlalchemy.orm import sessionmaker, Session, declarative_base
# from typing import List, Optional
# from pydantic import BaseModel
# import datetime
# import os
# import json

# # MySQLの接続情報（MySQL Connector/Python用のDSNに変更）
# DATABASE_URL = "mysql+mysqlconnector://user:password@db:3306/db?charset=utf8mb4"

# # SQLAlchemyのエンジンを作成
# engine = create_engine(DATABASE_URL, echo=True)

# # SessionLocalクラスを作成（各リクエストごとにDBセッションを生成）
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Baseクラスの作成
# Base = declarative_base()

# # ブログ投稿モデルの定義
# class BlogPost(Base):
#     __tablename__ = "article"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255), nullable=False)
#     summary150 = Column(String(200), nullable=False)
#     summary1000 = Column(String(1000), nullable=False)
#     content = Column(Text, nullable=False)
#     url = Column(String(255), nullable=False)
#     published_date = Column(Date, nullable=False)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)

# # Pydanticモデル
# class BlogPostSchema(BaseModel):
#     id: int
#     title: str
#     summary150: str
#     summary1000: str
#     content: str
#     url: str
#     published_date: datetime.date
#     created_at: datetime.datetime

#     class Config:
#         orm_mode = True

# # FastAPIアプリケーションの初期化
# app = FastAPI()

# app_env = os.getenv("FASTAPI_ENV", "development")
# if app_env == "development":
#     allow_credentials = False
#     origins = ["http://localhost:3000"]
# else:
#     pass

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=allow_credentials,
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
#     allow_headers=["Content-Type", "Authorization"],
# )

# # DBセッションを依存性として提供する関数
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # 全ての投稿を取得するエンドポイント
# @app.get("/test", response_model=List[BlogPostSchema])
# def read_articles(db: Session = Depends(get_db)):
#     posts = db.query(BlogPost).order_by(BlogPost.published_date.desc()).all()
#     posts_data = jsonable_encoder(posts)
#     json_data = json.dumps(posts_data, ensure_ascii=False)
#     return Response(
#         content=json_data,
#         media_type="application/json; charset=utf-8",
#     )

# class TopPageItem(BaseModel):
#     id: int
#     title: str
#     summary50: str
#     summary1000: str
#     content: str
#     url: str
#     published_date: str  # 日付はシンプルに文字列で扱っています
#     created_at: str

# @app.get("/TopPage", response_model=List[TopPageItem])
# def top_page():
#     dummy_data = [
#         {
#             "id": 0,
#             "title": "最新ニュース: テクノロジーの革新",
#             "summary50": "新たな技術が市場に衝撃を与える。",
#             "summary1000": (
#                 "本日のニュースでは、最新のテクノロジートレンドに関する詳細な分析をお届けします。"
#                 "AI、IoT、そしてブロックチェーン技術の急速な発展により、今後の産業構造が大きく変化することが期待されます。"
#             ),
#             "content": (
#                 "詳細記事: 新技術の導入事例、専門家のインタビュー、及び市場分析を通じて、"
#                 "今後の展望について考察します。"
#             ),
#             "url": "https://example.com/news/tech",
#             "published_date": "2025-02-23",
#             "created_at": "2025-02-23T14:19:38.266Z"
#         },
#         {
#             "id": 1,
#             "title": "経済ニュース: 市場動向レポート",
#             "summary50": "株式市場に変動、注目の経済指標も。",
#             "summary1000": (
#                 "本日の経済ニュースは、国内外の市場動向に焦点を当てたレポートです。"
#                 "主要株価指数の急変や、最新の経済指標、そして政府の経済政策に関する情報を詳細に分析しています。"
#             ),
#             "content": (
#                 "記事内容: 市場における最新のデータと、専門家による分析を基に、"
#                 "今後の投資戦略やリスクについて解説します。"
#             ),
#             "url": "https://example.com/news/economy",
#             "published_date": "2025-02-23",
#             "created_at": "2025-02-23T14:19:38.266Z"
#         },
#         {
#             "id": 2,
#             "title": "エンタメ: 映画レビュー特集",
#             "summary50": "今話題の最新映画を徹底レビュー。",
#             "summary1000": (
#                 "エンターテインメント分野では、最新公開の映画に関するレビューが注目を集めています。"
#                 "ストーリー、演技、映像美、そして音楽のクオリティに至るまで、総合的な評価を行いました。"
#             ),
#             "content": (
#                 "レビュー記事: 最新の話題作について、監督やキャストのコメント、映画の見どころを徹底分析します。"
#             ),
#             "url": "https://example.com/news/entertainment",
#             "published_date": "2025-02-23",
#             "created_at": "2025-02-23T14:19:38.266Z"
#         }
#     ]
#     return dummy_data

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='0.0.0.0', port=4000)