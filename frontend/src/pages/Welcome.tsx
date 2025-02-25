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
        TechShift
      </h1>
      <p style={{ fontSize: "1.5rem", maxWidth: "800px", marginBottom: "2rem" }}>
        忙しい毎日を送るあなたへ――『情報ふるい』は、ネット上に散らばる最新技術ニュースや情報を自動で集約・要約し、<br />
        あなたに本当に必要な情報だけを厳選してお届けする新感覚プラットフォームです。<br />
        学生や社会人の情報収集の手間を大幅に軽減し、技術への情熱をさらに高めるための最適なツールとして、<br />
        日々の学びと成長をサポートします。
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