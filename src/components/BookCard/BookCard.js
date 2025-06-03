import React from "react";
import './BookCard.css';

function BookCard({ book, onLearnMore, onExplain }) {
    return (
        <div className="book-card">
            <div className="star-icon" onClick={onExplain}>🔍</div>
            {book.thumbnail && (
                <img src={book.thumbnail} alt={book.title} className="book-image" />
            )}
            <div className="book-title">{book.title}</div>
            <div className="book-author">{book.author}</div>
            <button className="learn-more-btn" onClick={onLearnMore}>
                Learn More
            </button>
        </div>
    );
}

export default BookCard;
