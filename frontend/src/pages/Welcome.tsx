import React, { useEffect } from "react";
import "../pages/Welcome.css"
import { useFlash } from "../contexts/FlashProvider";

const WelcomePage: React.FC = () => {
  const { showFlash } = useFlash();

  useEffect(() => {
    const flashData = sessionStorage.getItem("flashMessage");
    if (flashData) {
      const { message, type, duration } = JSON.parse(flashData);
      showFlash(message, type, duration);
      sessionStorage.removeItem("flashMessage");
    }
  }, [showFlash]);

  // Get Started ボタンがクリックされたときの処理
  const handleGetStarted = async () => {
    try {
      const response = await fetch("http://localhost:4000/login", {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error("ログインURL取得エラー:", error);
    }
  };

  return (
    <div className="gradient-bg">
      <ul className="circles">
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
        <h1 style={{ fontSize: "3rem", marginBottom: "1rem" }}>
        InfoCompass
        </h1>
        <p style={{ fontSize: "1.5rem", maxWidth: "800px", marginBottom: "2rem" }}>
          忙しい毎日を送るあなたへ――『InfoCompass』は、ネット上に散らばる最新技術ニュースや情報を自動で集約・要約し、
          <br />
          あなたに本当に必要な情報だけを厳選してお届けする新感覚プラットフォームです。<br />
          学生や社会人の情報収集の手間を大幅に軽減し、技術への情熱をさらに高めるための最適なツールとして、
          <br />
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
          onClick={handleGetStarted}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f0f0f0";
            (e.currentTarget as HTMLButtonElement).style.transform = "scale(1.05)";
          }}
          onMouseLeave={(e) => {
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