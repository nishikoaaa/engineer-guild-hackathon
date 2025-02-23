ALTER DATABASE db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE account(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) COLLATE utf8mb4_unicode_ci NOT NULL,
    password VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS article (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    meta VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    google_links TEXT NOT NULL
);

ALTER TABLE article CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO article (title, content, meta, google_links)
VALUES
('記事1', 'これは記事1の本文です。', 'この記事はテスト用です。', 'https://example.com/article1'),
('記事2', 'これは記事2の本文です。', 'この記事もテスト用です。', '[\"https://example.com/article2\", \"https://example.com/article2\"]'),
('記事3', 'これは記事3の本文です。', 'このデータもテスト用です。', 'https://example.com/article3');

