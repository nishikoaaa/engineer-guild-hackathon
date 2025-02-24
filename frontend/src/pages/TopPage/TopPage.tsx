import React, { useEffect, useState } from "react";
import "./TopPage.css";

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

const TopPage: React.FC = () => {
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
    const fetchArticles = async () => {
        try {
        const response = await fetch(API_URL);
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

    if (loading) return <p className="loading">ローディング中...</p>;
    if (error) return <p className="error">エラー: {error}</p>;

    return (
    <div className="toppage">
        <h1>TopPageです</h1>
        <div className="articles">
        {articles.map((article) => (
            <div key={article.id} className="article-card">
                <h2 className="title">{article.title}</h2>
                <p>{article.summary50}</p>
                <p>
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                    記事を読む
                    </a>
                </p>
                <p>公開日: {new Date(article.published_date).toLocaleDateString()}</p>
            </div>
        ))}
        </div>
    </div>
    );
};

export default TopPage;
