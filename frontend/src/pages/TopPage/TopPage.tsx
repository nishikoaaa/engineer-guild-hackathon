import React, { useEffect, useState } from "react";
import "./TopPage.css";
import HeaderButtons from "../../components/HeaderButton";
import logo from "../../assets/logo.png";


interface Article {
  id: number;
  title: string;
  summary150: string;
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
        if (response.status === 401) {
          window.location.href = "http://localhost:3000";
          return;
        }
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

  // 記事クリック時のログ登録処理と記事遷移
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

  if (loading)
    return (
      <div className="loading-container">
        <div className="spinner-border text-light spinner-large" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <div className="loading-text">ローディング中です</div>
      </div>
    );
  if (error) return <p className="error">エラー: {error}</p>;

  return (
    <div className="TopPage">
      <div className="logo-container">
        <img src={logo} alt="Logo" className="logo" />
      </div>
      <div className="registration">
        <h1 className="sakuhinmei">InfoCompass</h1>
      </div>
      
      <nav className="menu-bar">
        <HeaderButtons />
      </nav>

      <div className="articles">
        {articles.map((article) => (
          <div
            key={article.id}
            className="article-card"
            onClick={() => {
              handleLogRead(article.id);
              window.open(article.url, "_blank");
            }}
            style={{ cursor: "pointer" }}
          >
            <div className="releasedate">
              <p>公開日: {new Date(article.published_date).toLocaleDateString()}</p>
            </div>
            <div className="articlemain">
              <h2 className="title">{article.title}</h2>
            </div>
            <div className="summary50words">
              <p>{article.summary150}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopPage;