ALTER DATABASE db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gmail VARCHAR(100) COLLATE utf8mb4_unicode_ci NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE account CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- サンプルデータの挿入（gmailのみ）
INSERT INTO account (gmail) VALUES 
    ('test@gmail.com'),
    ('test1@gmail.com');

-- article テーブルの作成
CREATE TABLE article (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    summary150 VARCHAR(200) NOT NULL,
    summary1000 VARCHAR(1000),
    content TEXT NOT NULL,
    url VARCHAR(255) NOT NULL,
    published_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE article CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- サンプルデータの挿入
INSERT INTO article (title, summary150, summary1000, content, url, published_date) VALUES
('新年の目標達成の秘訣', 
 '新年の目標達成法を紹介', 
 '新年に立てる目標の達成方法を解説します。年初に意気込んで目標を立てたものの、途中で挫折してしまう経験はありませんか？目標を達成するためには、具体的な計画を立てることが重要です。目標を小さなステップに分けて実行し、進捗を確認しながら軌道修正を行うことで、無理なく目標に近づけます。また、モチベーションを維持するためには、達成した際の自分を想像したり、定期的に自己評価を行うことが効果的です。さらに、目標を周囲に宣言することで、自分にプレッシャーをかけるのも一つの方法です。日々の小さな努力を積み重ねることが、最終的な成功へと繋がります。2025年を素晴らしい一年にするために、目標を達成するための具体的なアクションプランを立てましょう。', 
 '新年の目標達成には、まず具体的な計画を立てることが重要です。特に、目標を小さなステップに分けて、達成感を味わいながら進めることがポイントです。また、モチベーションを維持するためには、定期的に自己評価を行い、進捗を確認しましょう。...', 
 'https://example.com/article1', 
 '2025-01-01'),

('最新のテクノロジートレンド2025', 
 '2025年の注目技術を紹介', 
 '2025年に注目すべきテクノロジートレンドを詳しく解説します。今年はAIの進化がさらに加速し、IoTとの連携が強化される見込みです。特に、AIを活用した自動化技術がビジネスの生産性を飛躍的に向上させることが期待されています。また、ブロックチェーン技術の進化により、セキュリティの強化や取引の透明性が向上し、金融業界だけでなく多くの産業に変革をもたらしています。さらに、メタバースの普及に伴い、VR（バーチャルリアリティ）とAR（拡張現実）が日常生活に浸透しつつあります。これらの技術はエンターテインメントだけでなく、教育や医療の現場でも活用が進むでしょう。2025年は、これらのテクノロジーが生活をより便利に、より豊かに変えていく年になることが予想されます。', 
 'AIの進化が加速し、IoTとの連携が強化されています。自動化技術によりビジネスの生産性が飛躍的に向上し、ブロックチェーン技術は金融業界を中心に多くの産業に影響を与えています。...', 
 'https://example.com/article2', 
 '2025-02-15');

-- survey テーブルの作成
CREATE TABLE survey (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid INT NOT NULL,
    age INT NOT NULL,
    gender ENUM('男', '女', 'その他') NOT NULL,
    job VARCHAR(100) NOT NULL,
    preferred_article_detail TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_survey_account FOREIGN KEY (userid) REFERENCES account(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE survey CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- サンプルデータの挿入（useridはaccountのidに合わせる）
INSERT INTO survey (userid, age, gender, job, preferred_article_detail) VALUES
    (1, 25, '男', 'エンジニア', '技術系の記事をもっと読みたい。特にAI関連に興味がある。'),
    (2, 32, '女', 'マーケティング', 'マーケティング戦略やSNSの最新トレンドについて知りたい。');

-- read_log テーブルの作成
CREATE TABLE read_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    article_id INT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_read_log_article FOREIGN KEY (article_id) REFERENCES article(id)
);

CREATE TABLE favorite_sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    url VARCHAR(255) NOT NULL,
    CONSTRAINT fk_favorite_sites_account FOREIGN KEY (user_id) REFERENCES account(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE favorite_sites CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO favorite_sites (user_id, url) VALUES
    (1, 'https://www.google.com'),
    (1, 'https://www.youtube.com'),
    (2, 'https://www.twitter.com');

CREATE TABLE retrieved_urls (
  id INT AUTO_INCREMENT PRIMARY KEY,
  url VARCHAR(255) NOT NULL,
  retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE favorite_sites CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;