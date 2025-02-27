// LogoutButton.tsx
import React from "react";
import "../pages/TopPage/TopPage.css";
import { useFlash } from "../contexts/FlashProvider";

interface LogoutButtonProps {
    onLogout?: () => void;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({ onLogout }) => {
    const { showFlash } = useFlash();

    const handleLogout = () => {
        if (onLogout) {
            onLogout();
        } else {
            sessionStorage.setItem(
                "flashMessage",
                JSON.stringify({ message: "ログアウトしました", type: "success", duration: 3000})
            )
            window.location.href = "http://localhost:4000/logout";
        }
    };

    return (
        <button
            onClick={handleLogout}
            className="common-button"
        >
            ログアウト
        </button>
    );
};

export default LogoutButton;