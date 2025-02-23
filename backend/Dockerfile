# ベースイメージ
# FROM python:3.10-slim
FROM python:3.9.7

# 必要なパッケージをインストール
# RUN apt-get update && apt-get install -y \
#     sudo wget vim curl gawk make gcc \
#     chromium chromium-driver \
#     libnss3 \
#     libx11-xcb1 \
#     libxcomposite1 \
#     libxcursor1 \
#     libxi6 \
#     libxtst6 \
#     libxrandr2 \
#     libasound2 \
#     libpangocairo-1.0-0 \
#     libatk1.0-0 \
#     libatk-bridge2.0-0 \
#     libcups2 \
#     libdbus-glib-1-2 \
#     libgtk-3-0 \
#     libgbm-dev \
#     nodejs \
#     && apt-get clean

# RUN apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y locales apt-utils && \
#     sed -i -e 's/# ja_JP.UTF-8 UTF-8/ja_JP.UTF-8 UTF-8/' /etc/locale.gen && \
#     locale-gen && \
#     update-locale LANG=ja_JP.UTF-8

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

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