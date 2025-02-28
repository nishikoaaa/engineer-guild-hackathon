<div id="top"></div>

## 使用技術一覧

<p style="display: inline">
  <img src="https://img.shields.io/badge/-React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB">
  <img src="https://img.shields.io/badge/-FastAPI-009688.svg?logo=fastapi&style=for-the-badge">
  <img src="https://img.shields.io/badge/-MySQL-4479A1.svg?logo=mysql&style=for-the-badge&logoColor=white">
  <img src="https://img.shields.io/badge/-TypeScript-007ACC.svg?logo=typescript&style=for-the-badge">
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
</p>

## 目次

1. [サマリーマンについて](#サマリーマンについて)
2. [環境](#環境)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [開発環境構築](#開発環境構築)
5. [トラブルシューティング](#トラブルシューティング)

---

## サマリーマンについて

**アプリ名:** サマリーマン

**概要:**  
ユーザーのニーズに合わせたニュース記事や技術ブログなどを自動的に収集し、収集したコンテンツを要約して表示するサービスです。  
（AIエージェントを活用した RAG により、効率的な情報収集を実現）

**ターゲットユーザー:**  
日々の情報収集に多くの時間を取られているすべての人。特に、社会情勢や技術トレンドなどをいち早くキャッチアップする必要がある社会人や大学生を対象としています。

---

## 環境

以下の環境変数は、プロジェクトルートに配置する `.env` ファイルに記載してください。

| 変数名              | 役割                                  | デフォルト値                             | DEV 環境での値 |
| ------------------- | ------------------------------------- | ---------------------------------------- | -------------- |
| MYSQL_ROOT_PASSWORD | MySQL のルートパスワード              | rootpassword                             |                |
| MYSQL_DATABASE      | MySQL のデータベース名                | db                                       |                |
| MYSQL_USER          | MySQL のユーザ名                      | user                                     |                |
| MYSQL_PASSWORD      | MySQL のパスワード                    | password                                 |                |
| REDIRECT_URI        | 認証後のリダイレクト先 URI              | http://localhost:4000/login/callback     |                |
| OPENAI_API_KEY      | OpenAI API キー                       | （空欄）                                 |                |
| CLIENT_SECRET       | クライアントシークレット              | （空欄）                                 |                |

その他の環境変数については、必要に応じて追加してください。

---

## ディレクトリ構成

以下は、本プロジェクトのディレクトリ構造の一例です。

```bash
.
├── README.md
├── backend
│   ├── Dockerfile
│   ├── app
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── auth.py
│   │   ├── embedd.py
│   │   ├── getdate.py
│   │   ├── index_data
│   │   ├── main.py
│   │   ├── terminal_operation.py
│   │   ├── url_acquisition.py
│   │   └── web_Acquisition.py
│   └── requirements.txt
├── certbot
│   └── www
├── command.txt
├── docker-compose-prod.yml
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   │   ├── hackicon.png
│   │   └── index.html
│   ├── src
│   │   ├── App.tsx
│   │   ├── assets
│   │   ├── components
│   │   ├── contexts
│   │   ├── declaration.d.ts
│   │   ├── index.tsx
│   │   └── pages
│   ├── tsconfig.json
│   └── yarn.lock
├── mysql
│   ├── init.sql
│   └── my.cnf
└── nginx
    ├── conf.d
    │   └── default.conf
    └── ssl
        ├── accounts
        ├── archive
        ├── live
        └── renewal