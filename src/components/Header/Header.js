import React from "react";
import { useNavigate } from "react-router-dom";
import "./Header.css";
import accountIcon from "../../assets/account.svg";

function Header() {
    const navigate = useNavigate();

    return (
        <div className="page-header">
            <h1 className="page-title" onClick={() => navigate("/")}>
                Book Recommendation
            </h1>

            <div className="login-icon" onClick={() => navigate("/account")}>
                <img src={accountIcon} alt="Account" style={{ width: 40, height: 40 }} />
            </div>
        </div>
    );
}

export default Header;
