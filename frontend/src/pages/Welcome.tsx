import React from "react";

const WelcomePage: React.FC = () => {
  return (
    <div
      className="welcome-container"
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
        color: "#fff",
        textAlign: "center",
        padding: "2rem",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
      }}
    >
      <h1 style={{ fontSize: "3rem", marginBottom: "1rem" }}>
        Engineer Guild Hackathon
      </h1>
      <p style={{ fontSize: "1.5rem", maxWidth: "800px", marginBottom: "2rem" }}>
        ようこそ！このプラットフォームでは、最新の技術情報を共有し、エンジニア同士が繋がる場を提供します。<br />
        AI、IoT、ブロックチェーンなど、先端技術に関する記事やアンケート、レコメンド機能を通じて、<br />
        あなたの技術への情熱を刺激し、共に成長することを目指しています。
      </p>
      <button
        style={{
          padding: "1rem 2rem",
          fontSize: "1.25rem",
          borderRadius: "30px",
          border: "none",
          backgroundColor: "#fff",
          color: "#182848",
          cursor: "pointer",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          transition: "background-color 0.3s, transform 0.3s"
        }}
        onMouseEnter={e => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f0f0f0";
          (e.currentTarget as HTMLButtonElement).style.transform = "scale(1.05)";
        }}
        onMouseLeave={e => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#fff";
          (e.currentTarget as HTMLButtonElement).style.transform = "scale(1)";
        }}
      >
        Get Started
      </button>
    </div>
  );
};

export default WelcomePage;