/**
 * Admin View Toggle and Pagination
 * Handles switching between list and card views and pagination
 */

class AdminViewManager {
    constructor() {
        this.currentPage = 1;
        this.recordsPerPage = 20;

        // First set the default view
        this.initViewToggle();

        // Then calculate records and set up pagination
        this.totalRecords = document.querySelectorAll('.list-view tbody tr').length;
        this.totalPages = Math.ceil(this.totalRecords / this.recordsPerPage);

        // Initialize pagination and setup hover effects
        this.initPagination();
        this.setupCardHoverEffects();

        // Show first page of data immediately
        this.showPage(1);
    }

    /**
     * Initialize view toggle functionality
     */
    initViewToggle() {
        const listViewBtn = document.getElementById('listViewBtn');
        const cardViewBtn = document.getElementById('cardViewBtn');
        const listView = document.querySelector('.list-view');
        const cardView = document.querySelector('.card-view');

        if (listViewBtn && cardViewBtn && listView && cardView) {
            // Set default view based on screen size
            this.setDefaultView();

            // Handle list view button click
            listViewBtn.addEventListener('click', () => {
                listView.style.display = 'block';
                cardView.style.display = 'none';
                listViewBtn.classList.add('active');
                cardViewBtn.classList.remove('active');
                localStorage.setItem('adminViewPreference', 'list');
            });

            // Handle card view button click
            cardViewBtn.addEventListener('click', () => {
                listView.style.display = 'none';
                cardView.style.display = 'block';
                cardViewBtn.classList.add('active');
                listViewBtn.classList.remove('active');
                localStorage.setItem('adminViewPreference', 'card');
            });
        }
    }

    /**
     * Set default view based on screen size and saved preference
     */
    setDefaultView() {
        const listViewBtn = document.getElementById('listViewBtn');
        const cardViewBtn = document.getElementById('cardViewBtn');
        const listView = document.querySelector('.list-view');
        const cardView = document.querySelector('.card-view');

        if (listViewBtn && cardViewBtn && listView && cardView) {
            const savedPreference = localStorage.getItem('adminViewPreference');
            const isMobile = window.innerWidth < 768;

            // Default to card view on mobile, or if card view was previously selected
            if (isMobile || savedPreference === 'card') {
                listView.style.display = 'none';
                cardView.style.display = 'block';
                cardViewBtn.classList.add('active');
                listViewBtn.classList.remove('active');
            } else {
                listView.style.display = 'block';
                cardView.style.display = 'none';
                listViewBtn.classList.add('active');
                cardViewBtn.classList.remove('active');
            }
        }
    }

    /**
     * Initialize pagination functionality
     */
    initPagination() {
        const paginationContainer = document.querySelector('.pagination-container');
        if (!paginationContainer) return;

        this.renderPagination();

        // Handle window resize to adjust view
        window.addEventListener('resize', () => {
            this.setDefaultView();
        });
    }

    /**
     * Render pagination controls
     */
    renderPagination() {
        const paginationContainer = document.querySelector('.pagination-container');
        if (!paginationContainer) return;

        // If there are no pages or only one page, hide pagination
        if (this.totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        let paginationHTML = `
            <nav aria-label="Page navigation">
                <ul class="pagination justify-content-center">
                    <li class="page-item" id="prevPage">
                        <a class="page-link" href="#" aria-label="Previous">
                            <span aria-hidden="true">&laquo;</span>
                        </a>
                    </li>
        `;

        // Limit the number of page buttons shown
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

        // Adjust start page if we're near the end
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        // Add first page button if not included in the range
        if (startPage > 1) {
            paginationHTML += `
                <li class="page-item" data-page="1">
                    <a class="page-link" href="#">1</a>
                </li>
            `;

            // Add ellipsis if there's a gap
            if (startPage > 2) {
                paginationHTML += `
                    <li class="page-item disabled">
                        <a class="page-link" href="#">...</a>
                    </li>
                `;
            }
        }

        // Add page buttons for the current range
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}" data-page="${i}">
                    <a class="page-link" href="#">${i}</a>
                </li>
            `;
        }

        // Add last page button if not included in the range
        if (endPage < this.totalPages) {
            // Add ellipsis if there's a gap
            if (endPage < this.totalPages - 1) {
                paginationHTML += `
                    <li class="page-item disabled">
                        <a class="page-link" href="#">...</a>
                    </li>
                `;
            }

            paginationHTML += `
                <li class="page-item" data-page="${this.totalPages}">
                    <a class="page-link" href="#">${this.totalPages}</a>
                </li>
            `;
        }

        paginationHTML += `
                    <li class="page-item" id="nextPage">
                        <a class="page-link" href="#" aria-label="Next">
                            <span aria-hidden="true">&raquo;</span>
                        </a>
                    </li>
                </ul>
            </nav>
        `;

        paginationContainer.innerHTML = paginationHTML;

        // Add event listeners to pagination controls
        document.querySelectorAll('.pagination .page-item[data-page]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(item.getAttribute('data-page'));
                this.showPage(page);
            });
        });

        // Previous page button
        const prevPageBtn = document.getElementById('prevPage');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.currentPage > 1) {
                    this.showPage(this.currentPage - 1);
                }
            });
        }

        // Next page button
        const nextPageBtn = document.getElementById('nextPage');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.currentPage < this.totalPages) {
                    this.showPage(this.currentPage + 1);
                }
            });
        }
    }

    /**
     * Show specific page of records
     * @param {number} page - Page number to show
     */
    showPage(page) {
        // If there are no pages, don't do anything
        if (this.totalPages === 0) return;

        this.currentPage = page;

        // Re-render pagination to update the visible page numbers
        this.renderPagination();

        // Enable/disable prev/next buttons
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');

        if (prevPageBtn) {
            prevPageBtn.classList.toggle('disabled', page === 1);
        }

        if (nextPageBtn) {
            nextPageBtn.classList.toggle('disabled', page === this.totalPages);
        }

        // Calculate start and end indices
        const startIndex = (page - 1) * this.recordsPerPage;
        const endIndex = Math.min(startIndex + this.recordsPerPage, this.totalRecords);

        // Update list view
        const listRows = document.querySelectorAll('.list-view tbody tr');
        listRows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });

        // Update card view
        const cards = document.querySelectorAll('.desktop-card');
        cards.forEach((card, index) => {
            if (index >= startIndex && index < endIndex) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    /**
     * Setup hover effects for cards
     */
    setupCardHoverEffects() {
        const cards = document.querySelectorAll('.desktop-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new AdminViewManager();
});
