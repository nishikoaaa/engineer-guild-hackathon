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
            className="btn"
            style={{
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                color: "#fff",
                border: "none",
                padding: "8px 16px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.9rem",
                transition: "background-color 0.3s ease",
            }}
            onMouseEnter={(e) => 
                (e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.3)")
            }
            onMouseLeave={(e) => 
                (e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.2)")
            }
        >
            ログアウト
        </button>
    );
};

export default LogoutButton;