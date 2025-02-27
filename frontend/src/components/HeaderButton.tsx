import React from "react";
import RegisterSiteButton from "./RegisterSiteButton";
import LogoutButton from "./LogoutButton";

const HeaderButtons: React.FC = () => {
    return (
        <div
            style={{
                position: "absolute",
                top: "20px",
                right: "20px",
                display: "flex",
                alignItems: "center",
                gap: "10px",
            }}
        >
            <RegisterSiteButton />
            <LogoutButton />
        </div>
    );
};

export default HeaderButtons;