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
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
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
    published_date = Column(DateTime, nullable=True)  # 日時（時間まで保持）
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ------------------------------
# 状態管理用の型定義
# ------------------------------
class State(TypedDict):
    url: str                # 入力された記事のURL
    content: str            # スクレイピングで取得した記事本文
    basic_info: Dict        # 基本情報: title, summary150, published_date
    detailed_summary: str   # 約1000文字程度の詳細な要約
    detailed_keywords: List[str]  # 生成された重要キーワードリスト（1回目のみ取得）
    basic_attempt: int      # 基本情報生成の試行回数
    detailed_attempt: int   # 詳細要約生成の試行回数
    basic_status: str       # "success", "retry", "failed"（基本情報生成の評価結果）
    detailed_status: str    # "success", "retry", "failed"（詳細要約生成の評価結果）
    error: str              # エラー情報（任意）

# ------------------------------
# Node: 記事本文のスクレイピング
# ------------------------------
def scrape_content_node(state: State, config) -> State:
    url = state["url"]
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        state["error"] = f"requests エラー: {e}"
        return state
    if resp.status_code == 200:
        html = resp.text
    else:
        state["error"] = f"HTTP エラー: {resp.status_code}"
        return state
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    state["content"] = text
    print("[scrape_content] 記事本文を取得しました。")
    return state

# ------------------------------
# Node: 基本情報生成（タイトル、150字要約、公開日時）
# ------------------------------
def generate_basic_info_node(state: State, config) -> State:
    state["basic_attempt"] = state.get("basic_attempt", 0) + 1
    print(f"[generate_basic_info] 試行回数 {state['basic_attempt']} 回目、URL: {state['url']}")
    llm = ChatOpenAI(
        model_name="gpt-4o-mini-2024-07-18",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "以下の文章から、記事のタイトル、150文字程度の要約、公開日時を抽出してください。"
                "150程度の要約文は150字程度で確実に書かれているかを確認するため、プログラムで150字程度になっているかカウントしてください"
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
        print(f"[generate_basic_info] JSON パースエラー: {e}")
        parsed = {}
    if "summary" in parsed:
        parsed["summary150"] = parsed.pop("summary")
    else:
        parsed["summary150"] = ""
    state["basic_info"] = parsed
    print("[generate_basic_info] 基本情報を生成しました。")
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
        print(f"[evaluate_basic_info] 公開日時が有効です: {pub_date}")
    except Exception as e:
        state["basic_status"] = "retry"
        state["error"] = f"公開日時が無効です: {e}"
        print(f"[evaluate_basic_info] 公開日時が無効です: {e}")
    return state

# ------------------------------
# Node: 詳細要約生成（約1000字）と重要キーワード出力（1回目のみ重要キーワード出力）
# ------------------------------
def generate_detailed_summary_node(state: State, config) -> State:
    state["detailed_attempt"] = state.get("detailed_attempt", 0) + 1
    print(f"[generate_detailed_summary] 試行回数 {state['detailed_attempt']} 回目、URL: {state['url']}")
    llm = ChatOpenAI(
        model_name="gpt-4o-mini-2024-07-18",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
    if state.get("detailed_attempt", 0) == 1:
        # 1回目は、詳細な要約とともに重要キーワード（5個程度）を出力
        base_prompt = (
            "以下の文章から、記事の約1000文字程度の詳細な要約と、"
            "記事に関する重要なキーワードを5個程度抽出してください。"
            "出力はJSON形式とし、キーは 'summary' と 'keywords' を使用してください。"
            "例: {"
            "\"summary\": \"ここに約1000文字の要約文を記述します。\", "
            "\"keywords\": [\"キーワード1\", \"キーワード2\", \"キーワード3\", \"キーワード4\", \"キーワード5\"]"
            "}"
        )
    else:
        # 2回目以降は、重要キーワードの出力は省略し、1回目の結果を利用する
        base_prompt = (
            "以下の文章から、記事の約1000文字程度の詳細な要約を抽出してください。"
            "出力はプレーンテキストで返してください。"
        )
        if state.get("detailed_keywords"):
            extra_instruction = f"【注意】1回目に取得した重要キーワード: {', '.join(state['detailed_keywords'])} を必ず含めるようにしてください。"
            base_prompt += "\n" + extra_instruction
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=base_prompt),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    formatted_prompt = prompt_template.format_prompt(text=state["content"])
    messages = formatted_prompt.to_messages()
    result = llm.invoke(messages)
    raw_output = result.content.strip()
    if state.get("detailed_attempt", 0) == 1:
        json_text = re.sub(r"^```(?:json)?\s*", "", raw_output)
        json_text = re.sub(r"\s*```$", "", json_text)
        try:
            parsed = json.loads(json_text)
        except Exception as e:
            print(f"[generate_detailed_summary] JSON パースエラー: {e}")
            parsed = {}
        state["detailed_summary"] = parsed.get("summary", "")
        state["detailed_keywords"] = parsed.get("keywords", [])
    else:
        state["detailed_summary"] = raw_output
        # 重要キーワードは1回目の結果をそのまま使用する
    print("[generate_detailed_summary] 詳細な要約と重要キーワードを生成しました。")
    return state

# ------------------------------
# Node: 詳細要約の評価（重要キーワードが70%以上含まれているかチェック）
# ------------------------------
def evaluate_detailed_summary_node(state: State, config) -> State:
    summary = state.get("detailed_summary", "")
    keywords = state.get("detailed_keywords", [])
    # 期待するキーワード数は5個
    if len(keywords) != 5:
        state["detailed_status"] = "retry"
        state["error"] = f"期待する重要キーワードの数は5個ですが、取得されたのは {len(keywords)} 個です。"
        print(f"[evaluate_detailed_summary] 期待する重要キーワード数が得られません: {len(keywords)} 個")
        return state
    summary_lower = summary.lower()
    found_count = 0
    missing = []
    for kw in keywords:
        if kw.lower() in summary_lower:
            found_count += 1
        else:
            missing.append(kw)
    if found_count >= 4:
        state["detailed_status"] = "success"
        print(f"[evaluate_detailed_summary] 重要キーワードのうち {found_count}/5 が要約に含まれています。")
    else:
        state["detailed_status"] = "retry"
        state["error"] = f"重要キーワードのうち {found_count}/5 が含まれています。不足: {', '.join(missing)}"
        print(f"[evaluate_detailed_summary] 重要キーワードのうち {found_count}/5 が含まれていません。不足: {', '.join(missing)}")
    return state

# ------------------------------
# Node: 記事情報をデータベースに保存
# ------------------------------
def save_article_node(state: State, config) -> State:
    if state.get("basic_status") == "success" and state.get("detailed_status") == "success":
        db = SessionLocal()
        basic = state.get("basic_info", {})
        pub_date = None
        pub_date_str = basic.get("published_date", "")
        if pub_date_str:
            try:
                pub_date = datetime.datetime.fromisoformat(pub_date_str)
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
        print("[save_article] 記事情報をデータベースに保存しました。")
    else:
        print("[save_article] 生成が不成功のため、記事情報は保存されませんでした。")
    return state

# ------------------------------
# 条件付きエッジの関数
# ------------------------------
def basic_info_decision(state: State, config) -> str:
    if state.get("basic_status") == "success":
        return "generate_detailed_summary"
    elif state.get("basic_attempt", 0) >= 3:
        return "skip"
    else:
        return "generate_basic_info"

def detailed_summary_decision(state: State, config) -> str:
    if state.get("detailed_status") == "success":
        return "save_article"
    elif state.get("detailed_attempt", 0) >= 5:
        return "skip"
    else:
        return "generate_detailed_summary"

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

# 条件付きエッジ：基本情報の評価後の判断
graph_builder.add_conditional_edges("evaluate_basic_info", basic_info_decision)
# 条件付きエッジ：詳細要約の評価後の判断
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
        print("使い方: python web_acquisition_ver2.py <記事URL>")
        sys.exit(1)
    input_url = sys.argv[1].strip()
    initial_state: State = {
        "url": input_url,
        "content": "",
        "basic_info": {},
        "detailed_summary": "",
        "detailed_keywords": [],
        "basic_attempt": 0,
        "detailed_attempt": 0,
        "basic_status": "",
        "detailed_status": "",
        "error": ""
    }
    config = None
    graph = graph_builder.compile()
    final_state = graph.invoke(initial_state)
    print("処理が完了しました。")
