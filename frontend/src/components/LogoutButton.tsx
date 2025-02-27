// LogoutButton.tsx
import React from "react";

interface LogoutButtonProps {
  onLogout?: () => void;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({ onLogout }) => {
  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    } else {
      window.location.href = "http://localhost:4000/logout";
    }
  };

  return (
    <button
      onClick={handleLogout}
      style={{
        padding: "0.8rem 1.5rem",
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
    >
      ログアウト
    </button>
  );
};

export default LogoutButton;