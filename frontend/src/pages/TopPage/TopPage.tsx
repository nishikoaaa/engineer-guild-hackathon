import React, { useEffect, useState, useRef } from "react";
import "./TopPage.css";
import RegisterSiteButton from "../../components/RegisterSiteButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlay, faStop } from "@fortawesome/free-solid-svg-icons";
import HeaderButtons from "../../components/HeaderButton";

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

  // 現在読み上げ中かどうか
  const [isPlaying, setIsPlaying] = useState(false);
  // どの記事を読み上げ中か（記事ID）
  const [readingArticleId, setReadingArticleId] = useState<number | null>(null);
  // 現在の読み上げに使う SpeechSynthesisUtterance を保持
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // 記事一覧の取得
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

  // カードをクリックしたら記事URLを新規タブで開く + ログ登録
  const handleCardClick = async (articleId: number, url: string) => {
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
    } finally {
      window.open(url, "_blank");
    }
  };

  // 「読み上げ／停止」ボタンのクリック処理
  const handleSpeechToggle = (
    e: React.MouseEvent<HTMLButtonElement>,
    articleId: number,
    textToRead: string
  ) => {
    // カード全体へのクリックイベント（URLを開く処理）を止める
    e.stopPropagation();

    // すでに同じ記事を読み上げ中なら停止
    if (isPlaying && readingArticleId === articleId) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setReadingArticleId(null);
      return;
    }

    // 別の記事を読み上げ中の場合もキャンセル
    if (isPlaying && readingArticleId !== articleId) {
      window.speechSynthesis.cancel();
    }

    // 新しく読み上げ開始
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = "ja-JP";
    utterance.onend = () => {
      // 再生終了時にステートを戻す
      setIsPlaying(false);
      setReadingArticleId(null);
    };

    // いったん現在の読み上げはキャンセルしてから再生
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);

    // State更新
    utteranceRef.current = utterance;
    setIsPlaying(true);
    setReadingArticleId(articleId);
  };

  if (loading) return(
    <div className="background">
      <div className="spinner-box">
        <div className="circle-border">
          <div className="circle-core"></div>
        </div>
      </div>
    </div>
  );

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
            onClick={() => handleCardClick(article.id, article.url)}
            style={{ cursor: "pointer" }}
          >
            <div className="releasedate">
              <p>公開日: {new Date(article.published_date).toLocaleDateString()}</p>
            </div>
            <div className="articlemain">
              <h2 className="title">{article.title}</h2>
              <div className="picture">syashinn</div>
            </div>
            <div className="summary50words">
              <p>{article.summary150}</p>
            </div>

            {/* ▼ ここに再生/停止ボタンを追加 ▼ */}
            <button
              onClick={(e) =>
                handleSpeechToggle(e, article.id, article.summary1000)}
                className="article-audio-button"
                title={isPlaying && readingArticleId === article.id ? "停止" : "記事の要約の読み上げ"}
            >
              {isPlaying && readingArticleId === article.id ? (
                <FontAwesomeIcon
                  icon={faStop}
                  style={{
                    fontSize: "24px",
                    color: "#ccc",
                  }}
                />
              ) : (
                <FontAwesomeIcon
                  icon={faPlay}
                  style={{
                    fontSize: "24px",
                    color: "#ccc",
                  }} />
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopPage;