import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage

# SQLAlchemy のインポート
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
from dateutil.parser import isoparse  # 追加：dateutil.parser を利用

# .env から環境変数を読み込み
load_dotenv()
api_key = os.environ['OPENAI_API_KEY']

# MySQL の接続情報（適宜書き換えてください）
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/db?charset=utf8mb4"

# エンジン、セッション、Base の作成
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 既存テーブル「article」のモデル定義
class BlogPost(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary150 = Column(String(200), nullable=False)  # 抽出本文の先頭200文字など
    summary1000 = Column(String(1000), nullable=True)   # 後で追加するためNULL許容
    content = Column(Text, nullable=False)            # 記事本文全体
    url = Column(String(255), nullable=False)
    published_date = Column(Date, nullable=False)      # Date 型で保存
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# 要約対象の記事URL（例：Qiitaの記事）
url = "https://qiita.com/mzmz__02/items/95a32ca71728e5237ed5"

# URLからHTML取得（User-Agent 指定）
headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/115.0.0.0 Safari/537.36")
}
response = requests.get(url, headers=headers)
html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")

# サイトのタイトル取得（<title>タグ）
title = soup.title.get_text() if soup.title else "タイトルなし"

def get_published_date_ldjson(soup):
    published_date = None
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if "datePublished" in item and item["datePublished"]:
                published_date = item["datePublished"]
                return published_date
            elif "dateCreated" in item and item["dateCreated"]:
                published_date = item["dateCreated"]
            elif "dateModified" in item and item["dateModified"]:
                published_date = item["dateModified"]
    return published_date

def get_published_date_from_time(soup):
    time_elem = soup.find("time", itemprop="datepublished")
    if time_elem:
        if time_elem.has_attr("datetime"):
            return time_elem["datetime"]
        else:
            text = time_elem.get_text().strip()
            return text.replace("公開日:", "").strip()
    return None

def get_published_date_from_meta(soup):
    published_date = None
    meta_pub = soup.find("meta", property="article:published_time")
    if meta_pub and meta_pub.get("content"):
        published_date = meta_pub.get("content")
    else:
        meta_pub = soup.find("meta", attrs={"name": "datePublished"})
        if meta_pub and meta_pub.get("content"):
            published_date = meta_pub.get("content")
        else:
            meta_created = soup.find("meta", attrs={"name": "dateCreated"})
            if meta_created and meta_created.get("content"):
                published_date = meta_created.get("content")
            else:
                meta_mod = soup.find("meta", attrs={"name": "dateModified"})
                if meta_mod and meta_mod.get("content"):
                    published_date = meta_mod.get("content")
    return published_date

# 公開日時取得（優先順：ld+json > <time> > meta）
published_date = get_published_date_ldjson(soup)
if not published_date:
    published_date = get_published_date_from_time(soup)
if not published_date:
    published_date = get_published_date_from_meta(soup)

# 日付のパースと形式固定
if published_date:
    try:
        dt = isoparse(published_date)
        published_date_str = dt.strftime("%Y-%m-%dT%H:%M")
        published_date_date = dt.date()  # Date型に変換
    except Exception as e:
        print("日付のパースに失敗しました:", e)
        published_date_str = None
        published_date_date = None
else:
    published_date_str = None
    published_date_date = None

print("取得した公開日時:", published_date_str if published_date_str else "None")

# 本文抽出（Qiita の記事本文は <div id="personal-public-article-body"> 内）
content_div = soup.find("div", id="personal-public-article-body")
if content_div is None:
    print("記事本文が見つかりませんでした。<body>タグから抽出します。")
    content_div = soup.body
paragraphs = content_div.find_all("p")
text_data = "\n".join([p.get_text() for p in paragraphs])

# 要約生成（モデル名を "gpt-4o-mini-2024-07-18" に変更、存在しない場合は利用可能なモデルに変更）
llm = ChatOpenAI(
    model_name="gpt-4o-mini-2024-07-18",  
    temperature=0,
    openai_api_key=api_key
)
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=(
            "以下は、記事本文です。150文字程度で記事の概要をまとめてください。"
        )
    ),
    HumanMessagePromptTemplate.from_template("{text}")
])
formatted_prompt = prompt_template.format_prompt(text=text_data)
messages = formatted_prompt.to_messages()
result = llm.invoke(messages)
summary_text = result.content

# MySQL に保存（公開日時が取得できた場合のみ保存）
if not published_date_date:
    print("公開日時が取得できなかったため、レコードは追加しません。")
else:
    db = SessionLocal()
    new_post = BlogPost(
        url=url,
        title=title,
        summary150=text_data[:200],  # 先頭200文字を summary150 に
        summary1000=None,             # 後で追加するため NULL
        content=text_data,
        published_date=published_date_date
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    print("----- データベースに保存された最新のレコード -----")
    print("タイトル:", new_post.title)
    print("要約文 (summary150):", new_post.summary150)
    print("公開日時:", new_post.published_date)
    db.close()
