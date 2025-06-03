import React, { useEffect, useState } from "react";
import BookCard from "../BookCard/BookCard";
import Header from "../Header/Header";
import BookPopup from "../BookPopup/BookPopup";
import "./Account.css";
import accountIcon from "../../assets/account.svg";
import logoutIcon from "../../assets/logout.svg";

function UserAccount() {
    const [userInfo, setUserInfo] = useState({ username: "", email: "" });
    const [favorites, setFavorites] = useState([]);
    const [isRegisterMode, setIsRegisterMode] = useState(false);
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [selectedBook, setSelectedBook] = useState(null);

    const fetchUserInfo = async () => {
        const token = localStorage.getItem("token");
        if (!token) {
            setIsLoggedIn(false);
            return;
        }

        try {
            const res = await fetch("http://127.0.0.1:8080/logininfo", {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!res.ok) {
                localStorage.removeItem("token");
                setIsLoggedIn(false);
                return;
            }

            const data = await res.json();
            if (data.username && data.email) {
                setUserInfo({ username: data.username, email: data.email });
                setIsLoggedIn(true);
            }
        } catch {
            localStorage.removeItem("token");
            setIsLoggedIn(false);
        }
    };

    const fetchFavorites = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8080/userfavorites", {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            const data = await res.json();
            if (Array.isArray(data.favorites)) {
                setFavorites(data.favorites);
            }
        } catch {
            setFavorites([]);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        setIsLoggedIn(false);
    };

    const handleLogin = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8080/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ identifier: username, password })
            });
            const data = await response.json();
            if (response.ok && data.access_token) {
                localStorage.setItem("token", data.access_token);
                setErrorMessage("");
                await fetchUserInfo();
                await fetchFavorites();
                setIsLoggedIn(true);
            } else {
                setErrorMessage(data.detail || "Login failed");
            }
        } catch {
            setErrorMessage("Login error");
        }
    };

    const handleRegister = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8080/register/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password })
            });
            const data = await response.json();
            if (response.ok) {
                alert("Registered successfully");
                setIsRegisterMode(false);
                setErrorMessage("");
            } else {
                setErrorMessage(data.detail || "Register failed");
            }
        } catch {
            setErrorMessage("Register error");
        }
    };

    useEffect(() => {
        fetchUserInfo();
        fetchFavorites();
    }, []);

    if (!isLoggedIn) {
        return (
            <div className="account-page">
                <Header />
                <div className="account-card">
                    <h2>{isRegisterMode ? "Đăng Ký" : "Đăng Nhập"}</h2>
                    {isRegisterMode && (
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    )}
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    {errorMessage && <p className="error">{errorMessage}</p>}
                    <button onClick={isRegisterMode ? handleRegister : handleLogin}>
                        {isRegisterMode ? "Register" : "Login"}
                    </button>
                    <button onClick={() => {
                        setIsRegisterMode(!isRegisterMode);
                        setErrorMessage("");
                    }}>
                        {isRegisterMode ? "Đã có tài khoản? Đăng nhập" : "Chưa có tài khoản? Đăng ký"}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="account-page">
            <Header />
            <div className="account-card">
                <img src={accountIcon} alt="Avatar" className="avatar" />
                <div className="account-info">
                    <div className="info-row">
                        <span className="info-label">Username:</span>
                        <span className="info-value">{userInfo.username}</span>
                    </div>
                    <div className="info-row">
                        <span className="info-label">Email:</span>
                        <span className="info-value">{userInfo.email}</span>
                    </div>
                </div>
                <button className="logout-btn" onClick={handleLogout}>
                    <img src={logoutIcon} alt="Logout" />
                    Đăng xuất
                </button>
            </div>

            <div className="favorite-section">
                <h3>Sách yêu thích</h3>
                {favorites.length === 0 ? (
                    <p>No favorite book yet</p>
                ) : (
                    <div className="favorite-list">
                        {favorites.map((book, idx) => (
                            <BookCard
                                key={idx}
                                book={book}
                                onLearnMore={() => setSelectedBook(book)}
                                onExplain={() => {}}
                            />
                        ))}
                    </div>
                )}
            </div>

            {selectedBook && (
                <BookPopup
                    book={selectedBook}
                    onClose={() => setSelectedBook(null)}
                    onAddFavorite={() => {}}
                />
            )}
        </div>
    );
}

export default UserAccount;
