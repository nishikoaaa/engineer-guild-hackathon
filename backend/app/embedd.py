from openai import OpenAI
import openai
import pandas as pd
import numpy as np
import json
import re
import faiss
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage, Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.in_memory import InMemoryDocstore
from concurrent.futures import ThreadPoolExecutor
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from typing import List
import mysql.connector
from pydantic import BaseModel

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

# def read_articles():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute(
#             "SELECT id, title, summary150, summary1000, content, url, published_date, created_at "
#             "FROM article ORDER BY published_date DESC"
#         )
#         rows = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         print(rows)
#     except mysql.connector.Error as err:
#         raise HTTPException(status_code=500, detail=f"Database query error: {err}")

# 記事データを取得して article_list に格納する関数
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
        
        # データを article_list に格納
        article_list = []
        for row in rows:
            article_list.append([
                row["id"],
                row["title"],
                row["summary150"],
                row["summary1000"],
                row["content"],
                row["url"],
                row["published_date"],
                row["created_at"]
            ])
        
        print(f"{len(article_list)} 件の記事を取得しました。")
        return article_list
    except mysql.connector.Error as err:
        raise Exception(f"Database query error: {err}")

# .env ファイルを読み込む
load_dotenv()
# 変数を取得
key = os.getenv("OPENAI_API_KEY")
    
openai = OpenAI(
    api_key=key
)
# 記事データを取得
article_list = read_articles()

# OpenAI APIを用いてテキストをベクトル化する関数
def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    # response["data"] はリストなので、最初のembeddingを返す
    return response.data[0].embedding

# 各記事を1件ずつベクトル化する（例：記事タイトルと本文を連結）
embeddings = []
for article in article_list:
    text_to_embed = article[2] + "\n" + article[3]
    embedding = get_embedding(text_to_embed)
    embeddings.append(embedding)

# embeddings を numpy 配列に変換（FAISSは float32 の numpy 配列が必要）
embeddings_np = np.array(embeddings).astype('float32')

# FAISS のインデックスを作成（ここでは L2 距離を用いた平坦なインデックス）
dim = embeddings_np.shape[1]  # 埋め込みベクトルの次元数
index = faiss.IndexFlatL2(dim)
index.add(embeddings_np)
print("登録されたベクトル数:", index.ntotal)

# FAISS インデックスを保存
faiss.write_index(index, "faiss_index.faiss")
print("FAISS インデックスを保存しました。")