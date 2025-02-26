// TopPage.tsx
import React, { useEffect, useState } from "react";
import "./TopPage.css";
import RegisterSiteButton from "../../components/RegisterSiteButton"; // パスは実際のファイル位置に合わせて変更

interface Article {
  id: number;
  title: string;
  summary50: string;
  summary1000: string;
  content: string;
  url: string;
  published_date: string;
  created_at: string;
}

const API_URL = "http://localhost:4000/TopPage";
const LOG_API_URL = "http://localhost:4000/log_read";

const TopPage: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await fetch(API_URL, {
          method: "GET",
          credentials: "include",
          redirect: "follow",
          mode: "cors",
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Article[] = await response.json();
        setArticles(data);
      } catch (err: any) {
        setError(err.message || "エラーが発生しました");
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // 記事クリック時のログ登録処理
  const handleLogRead = async (articleId: number) => {
    try {
      const response = await fetch(LOG_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1, article_id: articleId }),
        credentials: "include",
        redirect: "follow",
        mode: "cors",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log("ログ登録完了");
    } catch (err: any) {
      console.error("ログ登録エラー:", err.message);
    }
  };

  if (loading) return <p className="loading">ローディング中...</p>;
  if (error) return <p className="error">エラー: {error}</p>;

  return (
    <div className="Background">
      <ul className="circles">
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
      <h1>TopPageです</h1>
      <div className="articles">
        {articles.map((article) => (
          <div key={article.id} className="article-card">
            <p>公開日: {new Date(article.published_date).toLocaleDateString()}</p>
            <div className="articlemain">
              <h2 className="title">{article.title}</h2>
              <div className="picture">syashinn</div>
            </div>
            <p>{article.summary50}</p>
            <p>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => handleLogRead(article.id)}
              >
                記事を読む
              </a>
            </p>
          </div>
        ))}
      </div>
      {/* 右上にサイト登録用フォームコンポーネントを表示 */}
      <RegisterSiteButton />
    </div>
  );
};

export default TopPage;