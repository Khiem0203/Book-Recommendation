import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import BookCard from "./components/BookCard/BookCard";
import BookPopup from "./components/BookPopup/BookPopup";
import Pagination from "./components/Pagination/Pagination";

function App() {
    const [query, setQuery] = useState("");
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedBook, setSelectedBook] = useState(null);
    const [explanation, setExplanation] = useState(null);

    const booksPerPage = 20;
    const totalPages = Math.ceil(books.length / booksPerPage);
    const indexOfLastBook = currentPage * booksPerPage;
    const indexOfFirstBook = indexOfLastBook - booksPerPage;
    const currentBooks = books.slice(indexOfFirstBook, indexOfLastBook);

    const searchBooks = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const response = await axios.get("http://127.0.0.1:8000/bookrcm", {
                params: { query, k: 1000 },
            });
            setBooks(response.data.results || []);
            setCurrentPage(1);
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
        setLoading(false);
    };

    const explainBook = async (book) => {
        setExplanation("Loading...");
        try {
            const response = await axios.post("http://127.0.0.1:8000/explain", {
                title: book.title,
                authors: book.authors,
                description: book.description,
            });
            setExplanation(response.data.reason);
        } catch (error) {
            setExplanation("Could not fetch explanation.");
        }
    };

    const handlePageChange = (page) => {
        if (page < 1 || page > totalPages) return;
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const getVisiblePages = () => {
        const visible = [];
        if (totalPages <= 10) {
            for (let i = 1; i <= totalPages; i++) visible.push(i);
        } else {
            if (currentPage <= 4) {
                visible.push(1, 2, 3, 4, 5, "...", totalPages);
            } else if (currentPage >= totalPages - 3) {
                visible.push(1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
            } else {
                visible.push(
                    1,
                    "...",
                    currentPage - 2,
                    currentPage - 1,
                    currentPage,
                    currentPage + 1,
                    currentPage + 2,
                    "...",
                    totalPages
                );
            }
        }
        return visible;
    };

    return (
        <div className="container">
            <h1>Book Recommendation</h1>
            <div className="search-bar">
                <input
                    type="text"
                    className="search-input"
                    placeholder="What would you like to read today? (e.g. love, AI, mystery...)"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button className="search-button" onClick={searchBooks}>
                    Get Recommendations
                </button>
            </div>

            {loading && <p>Loading...</p>}

            <ul className="book-list">
                {currentBooks.map((book, index) => (
                    <BookCard
                        key={index}
                        book={book}
                        onLearnMore={() => setSelectedBook(book)}
                        onExplain={() => explainBook(book)}
                    />
                ))}
            </ul>

            {books.length > 0 && (
                <Pagination
                    totalPages={totalPages}
                    currentPage={currentPage}
                    onPageChange={handlePageChange}
                    getVisiblePages={getVisiblePages}
                />
            )}

            {selectedBook && (
                <BookPopup
                    book={selectedBook}
                    onClose={() => setSelectedBook(null)}
                    onExplain={() => explainBook(selectedBook)}
                />
            )}

            {explanation && (
                <div className="chat-popup">
                    <strong>Why you'll like this book:</strong>
                    <p>{explanation}</p>
                    <button className="close-chat" onClick={() => setExplanation(null)}>
                        ✖
                    </button>
                </div>
            )}
        </div>
    );
}

export default App;
