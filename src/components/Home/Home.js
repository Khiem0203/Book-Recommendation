import React, { useState } from "react";
import { } from "react-router-dom";
import "./Home.css";
import BookCard from "../BookCard/BookCard";
import BookPopup from "../BookPopup/BookPopup";
import Pagination from "../Pagination/Pagination";
import Header from "../Header/Header";

function HomeContent() {
    const [query, setQuery] = useState("");
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedBook, setSelectedBook] = useState(null);
    const [explanation, setExplanation] = useState(null);
    const [suggestions, setSuggestions] = useState([]);

    const booksPerPage = 20;
    const totalPages = Math.ceil(books.length / booksPerPage);
    const currentBooks = books.slice((currentPage - 1) * booksPerPage, currentPage * booksPerPage);

    const fetchSuggestions = async (userQuery) => {
        try {
            const res = await fetch(`http://127.0.0.1:8080/suggestions?query=${userQuery}`);
            const data = await res.json();
            setSuggestions(data.suggestions || []);
        } catch (error) {
            console.error("Error fetching suggestions:", error);
        }
    };

    const searchBooks = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setSuggestions([]);
        try {
            const res = await fetch(`http://127.0.0.1:8080/bookrcm?query=${query}&k=1000`);
            const data = await res.json();
            setBooks(data.results || []);
            setCurrentPage(1);
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
        setLoading(false);
    };

    const explainBook = async (book) => {
        setExplanation("Loading...");
        try {
            const res = await fetch("http://127.0.0.1:8080/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: book.title,
                    author: book.author,
                    description: book.description
                })
            });
            const data = await res.json();
            setExplanation(data.reason);
        } catch {
            setExplanation("Could not fetch explanation.");
        }
    };

    const handleAddFavorite = async (bookId) => {
        const token = localStorage.getItem("token");
        if (!token) return alert("Vui lòng đăng nhập để thêm vào yêu thích!");

        try {
            const res = await fetch("http://127.0.0.1:8080/favorites/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ book_id: bookId })
            });

            if (res.ok) {
                alert("Đã thêm vào danh sách yêu thích!");
            } else {
                const data = await res.json();
                alert("Lỗi khi thêm sách: " + (data.detail || res.statusText));
            }
        } catch (err) {
            alert("Không thể kết nối tới server.");
            console.error(err);
        }
    };

    const handlePageChange = (page) => {
        if (page < 1 || page > totalPages) return;
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const getVisiblePages = () => {
        const pages = [];
        if (totalPages <= 10) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else if (currentPage <= 4) {
            pages.push(1, 2, 3, 4, 5, "...", totalPages);
        } else if (currentPage >= totalPages - 3) {
            pages.push(1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
        } else {
            pages.push(1, "...", currentPage - 2, currentPage - 1, currentPage, currentPage + 1, currentPage + 2, "...", totalPages);
        }
        return pages;
    };

    return (
        <div className="container">
            <Header />

            <div className="search-bar">
                <div className="autocomplete-container">
                    <input
                        type="text"
                        className="search-input"
                        placeholder="What would you like to read today?"
                        value={query}
                        onChange={(e) => {
                            const value = e.target.value;
                            setQuery(value);
                            if (value.length > 0) fetchSuggestions(value);
                            else setSuggestions([]);
                        }}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") searchBooks();
                        }}
                    />
                    {query.length > 0 && suggestions.length > 0 && (
                        <ul className="autocomplete-list">
                            {suggestions.map((s, idx) => (
                                <li key={idx} className="autocomplete-item" onClick={() => {
                                    setQuery(s.query);
                                    setSuggestions([]);
                                    searchBooks();
                                }}>
                                    {s.query}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
                <button className="search-button" onClick={searchBooks}>Get Recommendations</button>
            </div>

            {loading && <p>Loading...</p>}

            <ul className="book-list">
                {currentBooks.map((book, index) => (
                    <BookCard key={index} book={book} onLearnMore={() => setSelectedBook(book)} onExplain={() => explainBook(book)} />
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
                    onAddFavorite={handleAddFavorite}
                />
            )}

            {explanation && (
                <div className="chat-popup">
                    <strong>Bạn sẽ thích quyển sách này vì:</strong>
                    <p>{explanation}</p>
                    <button className="close-chat" onClick={() => setExplanation(null)}>✖</button>
                </div>
            )}
        </div>
    );
}

export default HomeContent;