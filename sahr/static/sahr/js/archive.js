class ArchiveApp {
    constructor() {
        this.currentPage = 1;
        this.rowsPerPage = 25;
        this.allPositions = [];
        this.filteredPositions = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadArchive();
    }

    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }

    setupEventListeners() {
        // Поиск в архиве
        const searchBtn = document.getElementById('archiveSearchBtn');
        const searchInput = document.getElementById('archiveSearch');
        
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => this.searchArchive());
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.searchArchive();
            });
        }

        // Пагинация
        document.getElementById('firstPage')?.addEventListener('click', () => this.goToPage(1));
        document.getElementById('prevPage')?.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        document.getElementById('nextPage')?.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        document.getElementById('lastPage')?.addEventListener('click', () => this.goToPage(this.getTotalPages()));
    }

    async loadArchive() {
        try {
            const response = await fetch('/sahr/archive_remove_positions/', {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) throw new Error('Ошибка загрузки архива');
            
            this.allPositions = await response.json();
            this.filteredPositions = [...this.allPositions];
            this.renderTable();
            
        } catch (error) {
            console.error('Ошибка загрузки архива:', error);
            alert('Ошибка загрузки архива');
        }
    }

    async searchArchive() {
        const searchInput = document.getElementById('archiveSearch');
        if (!searchInput) return;
        
        const query = searchInput.value.trim().toLowerCase();
        
        if (!query) {
            this.filteredPositions = [...this.allPositions];
        } else {
            this.filteredPositions = this.allPositions.filter(position => {
                return (
                    (position.article && position.article.toLowerCase().includes(query)) ||
                    (position.party && position.party.toLowerCase().includes(query)) ||
                    (position.address && position.address.toLowerCase().includes(query)) ||
                    (position.title && position.title.toLowerCase().includes(query))
                );
            });
        }
        
        this.currentPage = 1;
        this.renderTable();
    }

    getTotalPages() {
        return Math.ceil(this.filteredPositions.length / this.rowsPerPage);
    }

    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.renderTable();
    }

    formatDateTime(dateString) {
        if (!dateString) return '—';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return '—';
            return date.toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        } catch (error) {
            return '—';
        }
    }

    renderTable() {
        const tbody = document.getElementById('archiveTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        const startIndex = (this.currentPage - 1) * this.rowsPerPage;
        const endIndex = startIndex + this.rowsPerPage;
        const pageData = this.filteredPositions.slice(startIndex, endIndex);

        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center" style="padding: 3rem; color: var(--text-muted);">
                        <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>Ничего не найдено</p>
                    </td>
                </tr>
            `;
        } else {
            pageData.forEach(position => {
                const row = document.createElement('tr');
                
                const formattedDate = this.formatDateTime(position.date);
                const commentText = position.comment || '';
                
                row.innerHTML = `
                    <td class="text-truncate" title="${position.article || ''}">${position.article || '—'}</td>
                    <td class="text-truncate" title="${position.title || ''}">${position.title || '—'}</td>
                    <td class="text-truncate" title="${position.party || ''}">${position.party || '—'}</td>
                    <td>${position.address || '—'}</td>
                    <td>${formattedDate}</td>
                    <td class="text-truncate" title="${commentText}">${commentText || '—'}</td>
                    <td class="text-center">
                        <span class="status-badge status-unknown">
                            <i class="fas fa-archive"></i> Архив
                        </span>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }

        this.updatePagination();
    }

    updatePagination() {
        const totalPages = this.getTotalPages();
        const totalItems = this.filteredPositions.length;
        const startItem = totalItems > 0 ? (this.currentPage - 1) * this.rowsPerPage + 1 : 0;
        const endItem = Math.min(this.currentPage * this.rowsPerPage, totalItems);

        document.getElementById('paginationInfo').textContent = 
            `Показано ${startItem}-${endItem} из ${totalItems} записей`;

        document.getElementById('pageNumbers').textContent = 
            `${this.currentPage} из ${totalPages}`;

        document.getElementById('firstPage').disabled = this.currentPage === 1;
        document.getElementById('prevPage').disabled = this.currentPage === 1;
        document.getElementById('nextPage').disabled = this.currentPage === totalPages;
        document.getElementById('lastPage').disabled = this.currentPage === totalPages;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    new ArchiveApp();
});