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
# テーブル定義（article テーブル）
# ------------------------------
class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary150 = Column(String(200), nullable=False)
    summary1000 = Column(String(1000), nullable=True)
    content = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    published_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ------------------------------
# 状態管理用の型定義
# ------------------------------
class State(TypedDict):
    url: str                # 入力された記事のURL
    content: str            # スクレイピングで取得した記事本文
    basic_info: Dict        # 基本情報： title, summary150, published_date
    detailed_summary: str   # 1000字程度の詳細な要約
    basic_attempt: int      # 基本情報生成の試行回数
    detailed_attempt: int   # 詳細要約生成の試行回数
    basic_status: str       # "success", "retry", "failed"（基本情報）
    detailed_status: str    # "success", "retry", "failed"（詳細要約）
    error: str              # エラー情報（任意）

# ------------------------------
# Node: 記事本文のスクレイピング
# ------------------------------
def scrape_content_node(state: State, config) -> State:
    url = state["url"]
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        state["error"] = f"requests error: {e}"
        return state
    if resp.status_code == 200:
        html = resp.text
    else:
        state["error"] = f"HTTP error: {resp.status_code}"
        return state
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    state["content"] = text
    return state

# ------------------------------
# Node: 基本情報生成（タイトル、要約150、公開日時）
# ------------------------------
def generate_basic_info_node(state: State, config) -> State:
    state["basic_attempt"] = state.get("basic_attempt", 0) + 1
    print(f"[generate_basic_info] Attempt {state['basic_attempt']} for URL: {state['url']}")
    llm = ChatOpenAI(
        model_name="gpt-4o-mini-2024-07-18",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "以下の文章から、記事のタイトル、150文字程度の要約、公開日時を抽出してください。"
                "出力はJSON形式で、キーは 'title', 'summary', 'published_date' としてください。"
                "例: {"
                "\"title\": \"サンプルタイトル\", "
                "\"summary\": \"記事の要約テキスト。\", "
                "\"published_date\": \"2025-02-24T09:30\""
                "}"
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    formatted_prompt = prompt_template.format_prompt(text=state["content"])
    messages = formatted_prompt.to_messages()
    result = llm.invoke(messages)
    raw_output = result.content.strip()
    json_text = re.sub(r"^```(?:json)?\s*", "", raw_output)
    json_text = re.sub(r"\s*```$", "", json_text)
    try:
        parsed = json.loads(json_text)
    except Exception as e:
        print(f"[generate_basic_info] JSON parse error: {e}")
        parsed = {}
    state["basic_info"] = parsed
    return state

# ------------------------------
# Node: 基本情報の評価（公開日時の妥当性チェック）
# ------------------------------
def evaluate_basic_info_node(state: State, config) -> State:
    basic_info = state.get("basic_info", {})
    pub_date = basic_info.get("published_date", "")
    try:
        datetime.datetime.fromisoformat(pub_date)
        state["basic_status"] = "success"
        print(f"[evaluate_basic_info] Publication date valid: {pub_date}")
    except Exception as e:
        state["basic_status"] = "retry"
        state["error"] = f"Invalid publication date: {e}"
        print(f"[evaluate_basic_info] Invalid publication date: {e}")
    return state

# ------------------------------
# Node: 詳細要約生成（約1000字）
# ------------------------------
def generate_detailed_summary_node(state: State, config) -> State:
    state["detailed_attempt"] = state.get("detailed_attempt", 0) + 1
    print(f"[generate_detailed_summary] Attempt {state['detailed_attempt']} for URL: {state['url']}")
    llm = ChatOpenAI(
        model_name="gpt-4o-mini-2024-07-18",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "以下の文章から、記事の1000文字程度の詳細な要約を抽出してください。"
                "出力はプレーンテキストで返してください。"
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    formatted_prompt = prompt_template.format_prompt(text=state["content"])
    messages = formatted_prompt.to_messages()
    result = llm.invoke(messages)
    summary_text = result.content.strip()
    state["detailed_summary"] = summary_text
    return state

# ------------------------------
# Node: 詳細要約の評価（長さチェック：900～1100文字）
# ------------------------------
def evaluate_detailed_summary_node(state: State, config) -> State:
    summary = state.get("detailed_summary", "")
    if 900 <= len(summary) <= 1100:
        state["detailed_status"] = "success"
        print(f"[evaluate_detailed_summary] Summary length valid: {len(summary)} characters")
    else:
        state["detailed_status"] = "retry"
        state["error"] = f"Summary length invalid: {len(summary)} characters"
        print(f"[evaluate_detailed_summary] Summary length invalid: {len(summary)} characters")
    return state

# ------------------------------
# Node: 記事情報をデータベースに保存
# ------------------------------
def save_article_node(state: State, config) -> State:
    # 両方の生成が成功している場合のみ保存
    if state.get("basic_status") == "success" and state.get("detailed_status") == "success":
        db = SessionLocal()
        basic = state.get("basic_info", {})
        pub_date = None
        pub_date_str = basic.get("published_date", "")
        if pub_date_str:
            try:
                pub_date = datetime.datetime.fromisoformat(pub_date_str).date()
            except Exception as e:
                pub_date = None
        new_article = Article(
            title=basic.get("title", ""),
            summary150=basic.get("summary150", ""),
            summary1000=state.get("detailed_summary", ""),
            content=state["content"],
            url=state["url"],
            published_date=pub_date
        )
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        db.close()
        print("[save_article_node] Article saved to database.")
    else:
        print("[save_article_node] Article not saved due to unsuccessful generation.")
    return state

# ------------------------------
# LangGraph のグラフ構築
# ------------------------------
graph_builder = StateGraph(State)
graph_builder.add_node("scrape_content", scrape_content_node)
graph_builder.add_node("generate_basic_info", generate_basic_info_node)
graph_builder.add_node("evaluate_basic_info", evaluate_basic_info_node)
graph_builder.add_node("generate_detailed_summary", generate_detailed_summary_node)
graph_builder.add_node("evaluate_detailed_summary", evaluate_detailed_summary_node)
graph_builder.add_node("save_article", save_article_node)

# 条件付きエッジで基本情報の生成をループ
def basic_info_decision(state: State, config) -> str:
    if state.get("basic_status") == "success":
        return "generate_detailed_summary"
    elif state.get("basic_attempt", 0) >= 3:
        return "skip"
    else:
        return "generate_basic_info"
graph_builder.add_conditional_edges("evaluate_basic_info", basic_info_decision)

# 条件付きエッジで詳細要約の生成をループ
def detailed_summary_decision(state: State, config) -> str:
    if state.get("detailed_status") == "success":
        return "save_article"
    elif state.get("detailed_attempt", 0) >= 3:
        return "skip"
    else:
        return "generate_detailed_summary"
graph_builder.add_conditional_edges("evaluate_detailed_summary", detailed_summary_decision)

# Entry と Exit の設定
graph_builder.set_entry_point("scrape_content")
graph_builder.add_edge("scrape_content", "generate_basic_info")
graph_builder.add_edge("generate_basic_info", "evaluate_basic_info")
graph_builder.add_edge("generate_detailed_summary", "evaluate_detailed_summary")
graph_builder.set_finish_point("save_article")

# ------------------------------
# メイン処理: 単一のURLを処理して記事情報を取得し、DBに保存
# ------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python <script_name.py> <article_url>")
        sys.exit(1)
    input_url = sys.argv[1].strip()
    initial_state: State = {
        "url": input_url,
        "content": "",
        "basic_info": {},
        "detailed_summary": "",
        "basic_attempt": 0,
        "detailed_attempt": 0,
        "basic_status": "",
        "detailed_status": "",
        "error": ""
    }
    config = None
    graph = graph_builder.compile()
    final_state = graph.invoke(initial_state)
    print("処理完了。")
