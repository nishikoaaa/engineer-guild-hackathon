import React from "react";
import RegisterSiteButton from "./RegisterSiteButton";
import LogoutButton from "./LogoutButton";
import ProfileEditButton from "./ResetProfile";

const HeaderButtons: React.FC = () => {
    return (
        <div
            style={{
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
                padding: "1.3rem 1rem",
                background: "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
                margin: "10px 0",
            }}
        >
            <RegisterSiteButton />
            <div style={{ width: "19px" }} />
            <ProfileEditButton />
            <div style={{ width: "19px" }} />
            <LogoutButton />
            <div style={{ width: "10px" }} />
        </div>
    );
};

export default HeaderButtons;