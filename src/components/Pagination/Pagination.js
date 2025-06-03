import React from "react";
import './Pagination.css';

function Pagination({ totalPages, currentPage, onPageChange, getVisiblePages }) {
    return (
        <div className="pagination">
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="page-button arrow"
            >
                ⟨
            </button>

            {getVisiblePages().map((page, i) =>
                page === "..." ? (
                    <span key={`ellipsis-${i}`} className="page-ellipsis">...</span>
                ) : (
                    <button
                        key={page}
                        onClick={() => onPageChange(page)}
                        className={`page-button ${currentPage === page ? "active" : ""}`}
                    >
                        {page}
                    </button>
                )
            )}

            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="page-button arrow"
            >
                ⟩
            </button>
        </div>
    );
}

export default Pagination;
