import os
import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
# SQLAlchemy のインポート（MySQL 接続用）
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import List, Dict
import subprocess

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
# モデル定義: source_url テーブル
# ------------------------------
class SourceURL(Base):
    __tablename__ = "source_url"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False, unique=True)

# ------------------------------
# モデル定義: retrieved_urls テーブル
# ------------------------------
class RetrievedURL(Base):
    __tablename__ = "retrieved_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("source_url.id"), nullable=False)
    retrieved_url = Column(String(255), nullable=False, unique=True)
    retrieved_at = Column(DateTime, default=datetime.datetime.utcnow)

# テーブル作成（存在しなければ）
Base.metadata.create_all(bind=engine)

# ------------------------------
# 関数: source_url テーブルからプラットフォームURLとIDを辞書型で取得 {id: url}
# ------------------------------
def get_source_url_dict() -> Dict[int, str]:
    session = SessionLocal()
    records = session.query(SourceURL).all()
    session.close()
    url_dict = {record.id: record.url for record in records}
    return url_dict

# ------------------------------
# 関数: プラットフォームのサイトマップから全URLを取得（Firecrawl を使用）
# ------------------------------
def retrieve_urls_from_platform(platform_url: str) -> List[str]:
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    # まずは sitemapOnly=True で取得
    result = app.map_url(platform_url, params={"sitemapOnly": True, "includeSubdomains": True})
    if result.get("success"):
        urls = result.get("links", [])
    else:
        print("サイトマップの取得に失敗しました。")
        urls = []
    # 取得件数が100件未満の場合、sitemapOnly=Falseで再取得
    if len(urls) < 100:
        print(f"取得したURL数が {len(urls)} 件と少ないため、sitemapOnly=False にて再取得します。")
        result = app.map_url(platform_url, params={"sitemapOnly": False, "includeSubdomains": True})
        if result.get("success"):
            urls = result.get("links", [])
        else:
            print("sitemapOnly=False による再取得にも失敗しました。")
            urls = []
    return urls

# ------------------------------
# 関数: 新規のURLのみをデータベースに登録する
# ------------------------------
def insert_new_urls_for_platform(source_id: int, platform_url: str) -> List[str]:
    # Firecrawl を用いてサイトマップからURL一覧を取得
    retrieved_urls = retrieve_urls_from_platform(platform_url)
    # 重複しているURLを除去
    retrieved_urls = list(set(retrieved_urls))
    db = SessionLocal()
    # 既に登録されているURL（対象の source_id で登録済み）の集合を取得
    existing_urls = {record.retrieved_url for record in db.query(RetrievedURL).filter(RetrievedURL.source_id == source_id).all()}
    # 新規のURLのみ抽出
    new_urls = [url for url in retrieved_urls if url not in existing_urls]
    for url in new_urls:
        new_record = RetrievedURL(source_id=source_id, retrieved_url=url)
        db.add(new_record)
    db.commit()
    db.close()
    print(f"新規URL数: {len(new_urls)}")
    print("新規URLの登録が完了しました。")
    return new_urls

# ------------------------------
# メイン処理: 各プラットフォームの新規URLを登録し、それぞれのURLに対して web_Acquisition.py を実行する
# ------------------------------
def main():
    source_url_dict = get_source_url_dict()
    for source_id, platform_url in source_url_dict.items():
        print(f"処理中のプラットフォームID: {source_id}, URL: {platform_url}")
        new_urls = insert_new_urls_for_platform(source_id, platform_url)
        filtered_urls = []
        print("公開日時を検索します。")
        for url in new_urls:
            try:
                # getdate.py を引数付きで実行し、出力結果を取得
                result = subprocess.run(
                    ["python", "getdate.py", url],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = result.stdout.strip()
                if "記事は今日から3日以内に公開されています" in output:
                    filtered_urls.append(url)
                else:
                    print(f"→ このURLは3日以内ではないため除外されます。")
            except subprocess.CalledProcessError as e:
                print(f"URLの処理中にエラーが発生しました: {url}\nエラー内容: {e}")

        # 全てのURL処理後に、filtered_urls の件数を取得
        total_new = len(filtered_urls)
        print(f"このプラットフォームで新規記事URLは {total_new} 件です。")
        
        for idx, article_url in enumerate(filtered_urls, start=1):
            remaining = total_new - idx
            print(f"【進捗】{idx} 件目の記事URLを処理中。残り未実行URL数: {remaining} 件")
            subprocess.run(["python", "web_Acquisition.py", article_url])
            if idx >= 30:
                break

if __name__ == "__main__":
    main()
    print("処理完了しました")
