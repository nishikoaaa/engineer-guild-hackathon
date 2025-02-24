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
            use_unicode = True,
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
        },
        {
            "id": 3,
            "title": "スポーツ: 国際大会速報",
            "summary50": "世界が注目する熱戦が繰り広げられる。",
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
            "summary50": "政府が新たな政策を発表。",
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
            "summary50": "健康志向の生活が注目を浴びる。",
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
            "summary50": "注目企業が戦略を一新。",
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
            "summary50": "国際情勢における新たな動き。",
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
            "summary50": "暮らしに役立つ最新トレンド。",
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
            "summary50": "文化の多様性を体感する。",
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