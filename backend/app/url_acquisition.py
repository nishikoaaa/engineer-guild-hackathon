import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
# LangChain のインポート（ChatOpenAI, プロンプト用）
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from langgraph.graph import StateGraph
from typing import List, Dict
from typing_extensions import TypedDict

# SQLAlchemy のインポート（MySQL 接続用）
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# ------------------------------
# 環境変数の読み込み・API キー設定
# ------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
FirecrawlApp.api_key = FIRECRAWL_API_KEY

# ------------------------------
# MySQL の接続設定（適宜変更してください）
# ------------------------------
DATABASE_URL = "mysql+pymysql://user:password@db:3306/db?charset=utf8mb4"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------
# モデル定義: retrieved_urls テーブル
# ------------------------------
class RetrievedURL(Base):
    __tablename__ = "retrieved_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False, unique=True)
    retrieved_at = Column(DateTime, default=datetime.datetime.utcnow)

# テーブル作成（存在しなければ作成）
Base.metadata.create_all(bind=engine)

# ------------------------------
# URL 取得関数（Firecrawl を用いる）
# ------------------------------
def retrieve_urls_from_platform(platform_url: str) -> List[str]:
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    result = app.map_url(platform_url, params={"sitemapOnly": True,'includeSubdomains': True})
    if result.get("success"):
        urls = result.get("links", [])
    else:
        print("サイトマップの取得に失敗しました。")
        urls = []
    return urls

# ------------------------------
# 新規 URL をデータベースに登録する関数
# ------------------------------
def insert_new_urls(platform_url: str):
    # Firecrawl を用いてサイトマップからURL一覧を取得
    retrieved_urls = retrieve_urls_from_platform(platform_url)
    db = SessionLocal()
    # 既に登録されているURLをセットで取得
    existing_urls = {record.url for record in db.query(RetrievedURL).all()}
    # 新規のURLのみ抽出
    new_urls = [url for url in retrieved_urls if url not in existing_urls]
    for url in new_urls:
        new_record = RetrievedURL(url=url)
        db.add(new_record)
    db.commit()
    db.close()
    print(f"新規URL数: {len(new_urls)}")
    print("新規URLの登録が完了しました。")

# ------------------------------
# メイン処理
# ------------------------------
if __name__ == "__main__":
    platform_url = input("プラットフォームのURLを入力してください: ").strip()
    insert_new_urls(platform_url)
