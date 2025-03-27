import React from "react";
import './BookPopup.css'

function BookPopup({ book, onClose }) {
    return (
        <div className="book-popup-overlay" onClick={onClose}>
            <div className="book-popup" onClick={(e) => e.stopPropagation()}>
                <button className="popup-close" onClick={onClose}>Close</button>
                <h2>{book.title}</h2>
                <p><strong>Authors:</strong> {book.authors}</p>
                <p><strong>Genre:</strong> {book.categories || "Unknown"}</p>
                <p><strong>Rating:</strong> {book.average_rating || "N/A"}</p>
                <p><strong>Publication Year:</strong> {book.published_year || "Unknown"}</p>
                {book.thumbnail && <img src={book.thumbnail} alt="Book cover" />}
                <p style={{ marginTop: "1rem" }}>{book.description}</p>
                {book.amazon_link && (
                    <a
                        href={book.amazon_link}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                            display: "inline-block",
                            marginTop: "1rem",
                            background: "#000",
                            color: "#fff",
                            padding: "0.5rem 1rem",
                            borderRadius: "8px",
                            textDecoration: "none",
                        }}
                    >
                        Buy now at Amazon.com
                    </a>
                )}
            </div>
        </div>
    );
}

export default BookPopup;
