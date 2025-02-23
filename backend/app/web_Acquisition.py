import os
import sqlite3
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage

# .env ファイルから環境変数を読み込む
load_dotenv()
api_key = os.environ['OPENAI_API_KEY']

# 要約対象のURL（例: Qiitaの記事またはその他の日付情報が含まれる記事）
url = "https://qiita.com/mzmz__02/items/95a32ca71728e5237ed5"

# URLからHTMLを取得（User-Agent 指定）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)
html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")

# サイトのタイトル（<title>タグ）を抽出
title = soup.title.get_text() if soup.title else "タイトルなし"

def get_published_date_ldjson(soup):
    """
    <script type="application/ld+json"> 内の JSON をパースし、
    "datePublished" を優先的に取得し、なければ "dateCreated"、さらになければ "dateModified" を返す。
    """
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
    """
    記事内の <time> 要素（itemprop="datepublished"）から公開日時を取得する。
    datetime 属性があればそれを返し、なければテキストから抽出する。
    """
    time_elem = soup.find("time", itemprop="datepublished")
    if time_elem:
        if time_elem.has_attr("datetime"):
            return time_elem["datetime"]
        else:
            text = time_elem.get_text().strip()
            return text.replace("公開日:", "").strip()
    return None

def get_published_date_from_meta(soup):
    """
    ld+json や <time> 要素から取得できなかった場合のフォールバックとして、
    meta タグから "article:published_time"、"datePublished"、"dateCreated"、"dateModified" を探す。
    """
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

# まず ld+json から公開日時を取得
published_date = get_published_date_ldjson(soup)
# ld+json で取得できなければ <time> 要素から取得
if not published_date:
    published_date = get_published_date_from_time(soup)
# それでも取得できなければ meta タグから取得
if not published_date:
    published_date = get_published_date_from_meta(soup)

# 日付が取得できた場合、形式を "YYYY-MM-DDTHH:MM" に固定
if published_date:
    try:
        dt = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
        published_date = dt.strftime("%Y-%m-%dT%H:%M")
    except Exception as e:
        print("日付のパースに失敗しました:", e)


# 本文抽出（Qiita の記事本文は <div id="personal-public-article-body"> 内にあると仮定）
content_div = soup.find("div", id="personal-public-article-body")
if content_div is None:
    print("記事本文が見つかりませんでした。<body>タグから抽出します。")
    content_div = soup.body

paragraphs = content_div.find_all("p")
text_data = "\n".join([p.get_text() for p in paragraphs])

# ChatOpenAI を利用して要約（モデル名を "4o-mini" に変更）
llm = ChatOpenAI(
    model_name="gpt-4o-mini-2024-07-18",
    temperature=0,
    openai_api_key=api_key
)

prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=(
            "以下は、サイトから抽出した本文です。"
            "この本文の序論と結論をつなぎ合わせて150文字程度で出力して。"
        )
    ),
    HumanMessagePromptTemplate.from_template("{text}")
])
formatted_prompt = prompt_template.format_prompt(text=text_data)
messages = formatted_prompt.to_messages()
result = llm(messages)
summary_text = result.content

# SQLite データベースに接続
db_filename = "summaries.db"
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    title TEXT,
    extracted_text TEXT,
    summary TEXT,
    published_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

cursor.execute("PRAGMA table_info(summaries)")
columns = [info[1] for info in cursor.fetchall()]
if "title" not in columns:
    cursor.execute("ALTER TABLE summaries ADD COLUMN title TEXT")
if "published_date" not in columns:
    cursor.execute("ALTER TABLE summaries ADD COLUMN published_date TEXT")
conn.commit()

# 公開日時が取得できなかった場合はレコードを追加しない
print("取得した公開日時:", published_date)
if not published_date:
    print("公開日時が取得できなかったため、レコードは追加しません。")
else:
    cursor.execute(
        "INSERT INTO summaries (url, title, extracted_text, summary, published_date) VALUES (?, ?, ?, ?, ?)",
        (url, title, text_data, summary_text, published_date)
    )
    conn.commit()

cursor.execute("SELECT title, summary, published_date FROM summaries ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print("----- データベースに保存された最新のレコード -----")
    print("タイトル:", row[0])
    print("要約文:", row[1])
    print("公開日時:", row[2])
else:
    print("レコードが見つかりませんでした。")

conn.close()
