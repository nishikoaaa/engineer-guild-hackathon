FROM node:18

WORKDIR /app

# パッケージファイルをコピー
COPY package.json yarn.lock ./

# 依存関係をインストール
RUN yarn install

# アプリケーションコードをコピー
# COPY ./public /app/public
# COPY ./src /app/src
COPY . .

# 開発サーバーを起動
CMD ["yarn", "start"]
