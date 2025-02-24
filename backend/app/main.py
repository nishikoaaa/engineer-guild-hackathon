from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List, Optional
from pydantic import BaseModel
import datetime
import os
import json

# MySQLの接続情報（MySQL Connector/Python用のDSNに変更）
DATABASE_URL = "mysql+mysqlconnector://user:password@db:3306/db?charset=utf8mb4"

# SQLAlchemyのエンジンを作成
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocalクラスを作成（各リクエストごとにDBセッションを生成）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスの作成
Base = declarative_base()

# ブログ投稿モデルの定義
class BlogPost(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary150 = Column(String(200), nullable=False)
    summary1000 = Column(String(1000), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    published_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Pydanticモデル
class BlogPostSchema(BaseModel):
    id: int
    title: str
    summary150: str
    summary1000: str
    content: str
    url: str
    published_date: datetime.date
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# FastAPIアプリケーションの初期化
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

# DBセッションを依存性として提供する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 全ての投稿を取得するエンドポイント
@app.get("/test", response_model=List[BlogPostSchema])
def read_articles(db: Session = Depends(get_db)):
    posts = db.query(BlogPost).order_by(BlogPost.published_date.desc()).all()
    posts_data = jsonable_encoder(posts)
    json_data = json.dumps(posts_data, ensure_ascii=False)
    return Response(
        content=json_data,
        media_type="application/json; charset=utf-8",
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=4000)