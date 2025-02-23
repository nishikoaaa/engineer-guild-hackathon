import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

interface Article {
  id: number;
  title: string;
  summary50: string;
  summary1000: string;
  published_date: string;
  created_at: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000';

const BlogHome: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/test`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // データ型チェック
        if (!Array.isArray(data)) {
          throw new Error('Unexpected data format: Expected an array');
        }

        // created_at の降順でソート（新しい記事を上に）
        const sortedArticles = data.sort((a: Article, b: Article) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );

        setArticles(sortedArticles);
      } catch (err: any) {
        setError(err.message || 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>ローディング中...</div>;
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>
        <p>エラーが発生しました: {error}</p>
        <p>ページを再読み込みするか、後ほどお試しください。</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>ブログ記事一覧</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {articles.map((article) => (
          <div
            key={article.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
            }}
          >
            <h2 style={{ margin: '0 0 10px', color: '#007BFF' }}>
              <Link
                to={`/article/${article.id}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                {article.title}
              </Link>
            </h2>
            <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
              公開日: {new Date(article.published_date).toLocaleDateString()}
            </p>
            <p style={{ margin: '10px 0', color: '#333' }}>{article.summary50}</p>
            <p style={{ margin: '10px 0', color: '#555' }}>{article.summary1000}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BlogHome;

// import React, { useEffect, useState } from 'react';
// import { Link } from 'react-router-dom';

// interface Article {
//   id: number;
//   title: string;
//   created_at: string;
// }

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000';

// const BlogHome: React.FC = () => {
//   const [articles, setArticles] = useState<Article[]>([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     const fetchArticles = async () => {
//       try {
//         const response = await fetch(`${API_BASE_URL}/test`);
//         if (!response.ok) {
//           throw new Error(`HTTP error! status: ${response.status}`);
//         }

//         const data = await response.json();

//         // データ型チェック
//         if (!Array.isArray(data)) {
//           throw new Error('Unexpected data format: Expected an array');
//         }

//         // created_at の降順でソート（新しい記事を上に）
//         const sortedArticles = data.sort((a: Article, b: Article) => 
//           new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
//         );

//         setArticles(sortedArticles);

//         // setArticles(data);
//       } catch (err: any) {
//         setError(err.message || 'エラーが発生しました');
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchArticles();
//   }, []);

//   if (loading) {
//     return <div style={{ textAlign: 'center', marginTop: '50px' }}>ローディング中...</div>;
//   }

//   if (error) {
//     return (
//       <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>
//         <p>エラーが発生しました: {error}</p>
//         <p>ページを再読み込みするか、後ほどお試しください。</p>
//       </div>
//     );
//   }

//   return (
//     <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
//       <h1 style={{ textAlign: 'center', color: '#333' }}>ブログ記事一覧</h1>
//       <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
//         {articles.map((article) => (
//           <div
//             key={article.id}
//             style={{
//               border: '1px solid #ddd',
//               borderRadius: '8px',
//               padding: '16px',
//               boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
//               transition: 'transform 0.2s, box-shadow 0.2s',
//             }}
//             onMouseEnter={(e) => {
//               (e.currentTarget as HTMLElement).style.transform = 'scale(1.02)';
//               (e.currentTarget as HTMLElement).style.boxShadow =
//                 '0 6px 12px rgba(0, 0, 0, 0.2)';
//             }}
//             onMouseLeave={(e) => {
//               (e.currentTarget as HTMLElement).style.transform = 'scale(1)';
//               (e.currentTarget as HTMLElement).style.boxShadow =
//                 '0 4px 8px rgba(0, 0, 0, 0.1)';
//             }}
//           >
//             <h2 style={{ margin: '0 0 10px', color: '#007BFF' }}>
//               <Link
//                 to={`/article/${article.id}`}
//                 style={{ textDecoration: 'none', color: 'inherit' }}
//               >
//                 {article.title}
//               </Link>
//             </h2>
//             <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
//               作成日時: {new Date(article.created_at).toLocaleString()}
//             </p>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };

// export default BlogHome;
