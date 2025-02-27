import React from "react";
import RegisterSiteButton from "./RegisterSiteButton";
import LogoutButton from "./LogoutButton";

const HeaderButtons: React.FC = () => {
    return (
        <div
            style={{
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
                padding: "0rem 1rem",
                background: "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
            }}
        >
            <RegisterSiteButton />
            <div style={{ width: "10px" }} />
            <LogoutButton />
        </div>
    );
};

export default HeaderButtons;