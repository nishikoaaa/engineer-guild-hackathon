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
const LOGOUT_URL = "http://localhost:4000/logout";

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
          // 未認証の場合、ログインページに遷移
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

  // ログアウト処理
  const handleLogout = () => {
      window.location.href = LOGOUT_URL;
  };

  if (loading) return <p className="loading">ローディング中...</p>;
  if (error) return <p className="error">エラー: {error}</p>;

  return (
    <div
      className="TopPage"
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        background: "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
        padding: "2rem",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
      }}
    >
      <div className="registration">
        <h1 className="sakuhinmei">TopPageです</h1>
      </div>
      <button
        onClick={handleLogout}
        style={{
          backgroundColor: "#f44336",
          color: "white",
          padding: "10px 20px",
          marginTop: "20px",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer"
        }}
        >
          ログアウト
        </button>
      <div className="articles">
        {articles.map((article) => (
          <div key={article.id} className="article-card">
            <div className="releasedate">
              <p>公開日: {new Date(article.published_date).toLocaleDateString()}</p>
            </div>
            <div className="articlemain">
              <h2 className="title">{article.title}</h2>
              <div className="picture">syashinn</div>
            </div>
            <div className="summary50words">
              <p>{article.summary50}
              <button className="readbutton" style={{ display: "inline-block", marginLeft: "10px" }} onClick={() => handleLogRead(article.id)}>
                <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="readlink"
                >
                  記事を読む ▶
                  <span className="underline"></span>
                </a>
              </button>

              </p>

            </div>
            
          </div>
        ))}
      </div>
          <RegisterSiteButton />
      </div>
  );
};

export default TopPage;