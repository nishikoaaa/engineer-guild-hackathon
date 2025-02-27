// RegisterSiteButton.tsx
import React, { useState } from "react";

const RegisterSiteButton: React.FC = () => {
  const [showInput, setShowInput] = useState(false);
  const [urlInput, setUrlInput] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string>("");

  const handleButtonClick = () => {
    setShowInput(true);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setResultMessage("");

    if (!urlInput.trim()) {
      setResultMessage("URLを入力してください。");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:4000/regist_favorite_site", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput.trim() }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setResultMessage("登録できました");
      setUrlInput("");
      setShowInput(false); // 登録成功後にフォームを閉じる
    } catch (err: any) {
      console.error("登録エラー:", err.message);
      setResultMessage("登録できませんでした");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        margin: "20px",
        zIndex: 1000,
      }}
    >
      {showInput ? (
        <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <input
            type="url"
            placeholder="https://example.com"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            style={{
              padding: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              fontSize: "1rem",
            }}
            required
          />
          <button
            type="submit"
            style={{
              padding: "0.6rem 1rem",
              fontSize: "1rem",
              borderRadius: "20px",
              border: "none",
              backgroundColor: "#fff",
              color: "#182848",
              cursor: "pointer",
              boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
              transition: "background-color 0.3s, transform 0.3s",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f0f0f0";
              (e.currentTarget as HTMLButtonElement).style.transform = "scale(1.05)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#fff";
              (e.currentTarget as HTMLButtonElement).style.transform = "scale(1)";
            }}
            disabled={loading}
          >
            {loading ? "登録中..." : "送信"}
          </button>
        </form>
      ) : (
        <button
          onClick={handleButtonClick}
          className="common-button"
        >
          サイトを登録する
        </button>
      )}
      {resultMessage && (
        <p style={{ color: resultMessage === "登録できました" ? "green" : "red", marginTop: "0.5rem" }}>
          {resultMessage}
        </p>
      )}
    </div>
  );
};

export default RegisterSiteButton;