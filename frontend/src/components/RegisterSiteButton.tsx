import React, { useState } from "react";

const RegisterSiteButton: React.FC = () => {
  const [showInput, setShowInput] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState("");

  const handleRegisterClick = () => {
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
        credentials: "include",
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
    // 外側の div の余白を削除または縮小
    <div style={{ margin: "0", zIndex: 1000 }}>
      {showInput ? (
        <form
          onSubmit={handleSubmit}
          className="dropdown-item"
          style={{ maxWidth: "250px", width: "100%" }} // 幅を制限
        >
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
              width: "100%",
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
              marginTop: "0.5rem",
            }}
            disabled={loading}
          >
            {loading ? "登録中..." : "送信"}
          </button>
          {resultMessage && (
            <p style={{ color: resultMessage === "登録できました" ? "green" : "red", marginTop: "0.5rem" }}>
              {resultMessage}
            </p>
          )}
        </form>
      ) : (
        <span
          className="dropdown-item"
          style={{ cursor: "pointer" }}
          onClick={handleRegisterClick}
        >
          サイトを登録する
        </span>
      )}
    </div>
  );
};

export default RegisterSiteButton;