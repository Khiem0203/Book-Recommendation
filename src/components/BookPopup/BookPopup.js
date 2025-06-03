import React, { useEffect, useState } from "react";
import './BookPopup.css';
import CloseIcon from "../../assets/close.svg";

function BookPopup({ book, onClose }) {
    const [showFullDesc, setShowFullDesc] = useState(false);
    const [isFavorite, setIsFavorite] = useState(false);

    const shouldTruncate = book.description.length > 400;
    const visibleDescription = showFullDesc || !shouldTruncate
        ? book.description
        : book.description.slice(0, 400) + "...";

    const bookId = book.id ?? book.book_id;

    useEffect(() => {
        const checkFavorite = async () => {
            const token = localStorage.getItem("token");
            if (!token || !bookId) return;

            try {
                const res = await fetch(`http://127.0.0.1:8080/is_favorite/${bookId}`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                const data = await res.json();
                setIsFavorite(data.is_favorite === true);
            } catch (err) {
                console.error("Failed to check favorite:", err);
            }
        };

        checkFavorite();
    }, [bookId]);

    const toggleFavorite = async () => {
        const token = localStorage.getItem("token");
        if (!token || !bookId) {
            alert("Vui lòng đăng nhập để thao tác.");
            return;
        }

        try {
            if (isFavorite) {
                const res = await fetch(`http://127.0.0.1:8080/favorites/${bookId}`, {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (res.ok) {
                    setIsFavorite(false);
                } else {
                    const data = await res.json();
                    alert(data.detail || "Không thể bỏ lưu sách.");
                }
            } else {
                const res = await fetch(`http://127.0.0.1:8080/favorites/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`
                    },
                    body: JSON.stringify({ book_id: bookId })
                });

                if (res.ok) {
                    setIsFavorite(true);
                } else {
                    const data = await res.json();
                    alert(data.detail || "Không thể lưu sách.");
                }
            }
        } catch (err) {
            console.error("Lỗi khi toggle favorite:", err);
        }
    };

    return (
        <div className="book-popup-overlay" onClick={onClose}>
            <div className="book-popup" onClick={(e) => e.stopPropagation()}>
                <img
                    src={CloseIcon}
                    alt="Close"
                    style={{ width: 32, height: 32 }}
                    className="popup-close"
                    onClick={onClose}
                />

                <h2>{book.title}</h2>
                <p><strong>Tác giả:</strong> {book.author}</p>
                <p><strong>Thể loại:</strong> {book.categories || "Unknown"}</p>
                <p><strong>Ngôn ngữ:</strong> {book.language || "Unknown"}</p>
                <p><strong>Năm xuất bản:</strong> {book.publishing_year || "Unknown"}</p>
                <p><strong>Nhà xuất bản :</strong> {book.publisher || "Unknown"}</p>
                <p><strong>Số trang:</strong> {book.num_pages || "Unknown"}</p>

                {book.thumbnail && (
                    <img
                        src={book.thumbnail}
                        alt="Book cover"
                        className="popup-thumbnail"
                    />
                )}

                <p className="popup-description">{visibleDescription}</p>

                {shouldTruncate && (
                    <div className="toggle-description-container">
                        <span
                            className="toggle-description"
                            onClick={() => setShowFullDesc(!showFullDesc)}
                        >
                            {showFullDesc ? "Thu gọn ▲" : "Xem thêm ▼"}
                        </span>
                    </div>
                )}

                <div className="button-group">
                    {book.link && (
                        <button
                            className="popup-buy-link"
                            onClick={() => window.open(book.link, "_blank")}
                        >
                            Mua ngay tại Fahasa.com
                        </button>
                    )}
                    <button
                        className="popup-favorite-button"
                        onClick={toggleFavorite}
                    >
                        {isFavorite ? "Bỏ lưu" : "Lưu sách"}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default BookPopup;
