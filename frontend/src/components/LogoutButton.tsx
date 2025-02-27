import React from "react";
import "../pages/TopPage/TopPage.css";

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
    <span
      className="dropdown-item"
      style={{ cursor: "pointer" }}
      onClick={handleLogout}
    >
      ログアウト
    </span>
  );
};

export default LogoutButton;