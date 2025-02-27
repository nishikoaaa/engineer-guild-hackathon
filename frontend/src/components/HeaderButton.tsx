import React from "react";
import RegisterSiteButton from "./RegisterSiteButton";
import LogoutButton from "./LogoutButton";

const HeaderButtons: React.FC = () => {
  return (
    <nav className="navbar navbar-expand-lg bg-body-tertiary">
      <div className="container-fluid">
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <RegisterSiteButton />
            </li>
            <li className="nav-item">
              <LogoutButton />
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default HeaderButtons;