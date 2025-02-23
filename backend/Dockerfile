# ベースイメージ
FROM python:3.10

# 作業ディレクトリ設定
WORKDIR /app

# 必要なファイルをコピー
COPY ./app /app/app
COPY requirements.txt .

# Python依存関係をインストール
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# FastAPIを起動するためのポートを公開
EXPOSE 4000

# アプリケーションの起動コマンド（FastAPI）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]