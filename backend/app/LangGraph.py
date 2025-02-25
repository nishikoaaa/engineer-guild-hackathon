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
    summary1000 = Column(String(1000), nullable=True)  # 未実装なので NULL
    content = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    published_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# テーブルが存在しない場合に作成（既に存在すれば問題ありません）
Base.metadata.create_all(bind=engine)

# ------------------------------
# 状態管理用の型定義
# ------------------------------
class State(TypedDict):
    article_info: Dict
    urls: List[str]
    current_url_index: int
    current_url: str
    evaluation_result: str
    evaluation_error: str
    trial_count: int
    articles_data: List[Dict]

# ------------------------------
# Node: サイトマップの取得
# ------------------------------
def get_sitemap_node(state: State, config) -> State:
    platform_url = "https://www.gizmodo.jp/"
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    map_result = app.map_url(platform_url, params={'includeSubdomains': True})
    if map_result.get("success"):
        sitemap_urls = map_result.get("links", [])
    else:
        sitemap_urls = []
        print("サイトマップの取得に失敗しました。")
    # ".html" で終わるURLのみ抽出
    filtered_urls = [url for url in sitemap_urls if url.endswith('.html')]
    state["urls"] = filtered_urls
    state["current_url_index"] = 0
    print(f"取得した記事URL数: {len(filtered_urls)}")
    return state


# ------------------------------
# Node: LLM による記事情報の生成（1記事分）
# ------------------------------
def generate_article_info(state: State, config) -> State:
    url = state["urls"][state["current_url_index"]]
    state["current_url"] = url
    state["trial_count"] = state.get("trial_count", 0) + 1
    print(f"[generate_article_info] 試行回数: {state['trial_count']} | URL: {url}")
    
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        print(f"[generate_article_info] requests エラー: {e}")
        state["generation_status"] = "skip"
        state["generation_error"] = str(e)
        return state

    if resp.status_code == 200:
        html_content = resp.text
    else:
        print(f"[generate_article_info] HTTPエラー: Status code {resp.status_code}")
        state["generation_status"] = "skip"
        state["generation_error"] = f"HTTP status: {resp.status_code}"
        return state

    soup = BeautifulSoup(html_content, "html.parser")
    content = soup.get_text(separator="\n", strip=True)

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
    
    formatted_prompt = prompt_template.format_prompt(text=content)
    messages = formatted_prompt.to_messages()
    result = llm.invoke(messages)
    
    raw_output = result.content.strip()
    json_text = re.sub(r"^```(?:json)?\s*", "", raw_output)
    json_text = re.sub(r"\s*```$", "", json_text)
    
    try:
        parsed_output = json.loads(json_text)
    except Exception as e:
        print(f"[generate_article_info] JSONパースエラー: {e}")
        parsed_output = {}
    
    if "summary" in parsed_output:
        parsed_output["summary150"] = parsed_output.pop("summary")
    else:
        parsed_output["summary150"] = ""
    
    parsed_output["content"] = content
    parsed_output["url"] = url
    
    state["article_info"] = parsed_output
    state["generation_status"] = "success"
    return state

# ------------------------------
# Node: 生成された記事情報の評価（公開日時の妥当性チェック）
# ------------------------------
def evaluate_article_info(state: State, config) -> State:
    if state.get("generation_status") != "success":
        return state

    article_info = state.get("article_info", {})
    published_date = article_info.get("published_date", "")
    try:
        datetime.datetime.fromisoformat(published_date)
        state["evaluation_status"] = "success"
        print(f"[evaluate_article_info] 評価成功: {published_date}")
    except Exception as e:
        state["evaluation_status"] = "retry"
        state["evaluation_error"] = str(e)
        print(f"[evaluate_article_info] 評価失敗: {e}")
    return state

# ------------------------------
# Node: URL をスキップする（生成・評価がうまくいかない場合）
# ------------------------------
def skip_article(state: State, config) -> State:
    print(f"[skip_article] URL {state['current_url']} をスキップします。")
    return state

# ------------------------------
# 条件付きエッジのための判断関数
# ------------------------------
def evaluation_decision(state: State, config) -> str:
    if state.get("generation_status") == "skip":
        return "skip_article"
    elif state.get("evaluation_status") == "success":
        return "save_article_info"
    else:
        print("[evaluation_decision] 再生成に回します。")
        return "generate_article_info"

# ------------------------------
# Node: 生成された記事情報を MySQL (SQLAlchemy 経由) に保存
# ------------------------------
def save_article_info(state: State, config) -> State:
    print("[save_article_info] 記事情報をデータベースに保存します（MySQL）")
    db = SessionLocal()
    
    article = state.get("article_info", {})
    title = article.get("title", "")
    summary150 = article.get("summary150", "")
    content = article.get("content", "")
    url = article.get("url", "")
    published_date_str = article.get("published_date", "")
    
    # 日付文字列が存在する場合は Date 型に変換
    published_date = None
    if published_date_str:
        try:
            published_date = datetime.datetime.fromisoformat(published_date_str).date()
        except Exception as e:
            print(f"[save_article_info] 公開日時のパースエラー: {e}")
            published_date = None

    new_article = Article(
        title=title,
        summary150=summary150,
        summary1000=None,  # 未実装のため NULL とする
        content=content,
        url=url,
        published_date=published_date
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    db.close()
    
    state.setdefault("articles_data", []).append(article)
    print("[save_article_info] 保存完了。")
    return state

# ------------------------------
# サブプロセス: 1記事分の処理（生成→評価→保存）
# ------------------------------
def process_single_article(state: State, config) -> State:
    while True:
        state = generate_article_info(state, config)
        state = evaluate_article_info(state, config)
        decision = evaluation_decision(state, config)
        if decision == "save_article_info":
            state = save_article_info(state, config)
            break
        elif decision == "skip_article":
            state = skip_article(state, config)
            break
        else:
            continue
    return state

# ------------------------------
# Node: 全記事の処理をループする
# ------------------------------
def loop_process_node(state: State, config) -> State:
    while state["current_url_index"] < len(state["urls"]):
        print(f"----- URL {state['current_url_index']+1} / {len(state['urls'])} を処理中 -----")
        state = process_single_article(state, config)
        state["current_url_index"] += 1
    return state

# グラフ構築（各ノードの追加・エッジ設定）
graph_builder = StateGraph(State)
graph_builder.add_node("get_sitemap_node", get_sitemap_node)
graph_builder.add_node("loop_process_node", loop_process_node)
graph_builder.set_entry_point("get_sitemap_node")
graph_builder.add_edge("get_sitemap_node", "loop_process_node")
graph_builder.set_finish_point("loop_process_node")

# ------------------------------
# メイン処理
# ------------------------------
if __name__ == "__main__":
    initial_state: State = {
        "article_info": {},
        "urls": [],
        "current_url_index": 0,
        "current_url": "",
        "evaluation_result": "",
        "evaluation_error": "",
        "trial_count": 0,
        "articles_data": []
    }
    config = None
    graph = graph_builder.compile()
    final_state = graph.invoke(initial_state)
    print(f"全生成（試行）回数: {final_state.get('trial_count', 0)}")
