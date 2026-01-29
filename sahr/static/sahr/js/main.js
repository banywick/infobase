class SahrApp {
    constructor() {
        this.currentPage = 1;
        this.rowsPerPage = 25;
        this.sortField = 'id';
        this.sortDirection = 'asc';
        this.allPositions = [];
        this.filteredPositions = [];
        this.totalPositions = 0;
        this.inBasePositions = 0;
        this.editingId = null;
        this.deletingId = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadAllPositions();
        this.updateStats();
        this.setupSorting();
    }

    getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    async fetchWithCSRF(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options });
    }

    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        notifications.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    setupEventListeners() {
        // Поиск
        document.getElementById('searchBtn').addEventListener('click', () => this.searchPositions());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchPositions();
        });

        // Пагинация
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());
        document.getElementById('rowsPerPage').addEventListener('change', (e) => {
            this.rowsPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.renderTable();
        });

        // Кнопки пагинации
        document.getElementById('firstPage').addEventListener('click', () => this.goToPage(1));
        document.getElementById('prevPage').addEventListener('click', () => this.goToPage(this.currentPage - 1));
        document.getElementById('nextPage').addEventListener('click', () => this.goToPage(this.currentPage + 1));
        document.getElementById('lastPage').addEventListener('click', () => this.goToPage(this.getTotalPages()));

        // Фильтр таблицы
        document.getElementById('tableFilter').addEventListener('input', (e) => {
            this.filterTable(e.target.value);
        });

        // Резервное копирование
        document.getElementById('backupBtn').addEventListener('click', () => this.downloadBackup());

        // Вкладки
        document.getElementById('mainTabBtn').addEventListener('click', () => this.switchTab('main'));
        document.getElementById('archiveTabBtn').addEventListener('click', () => this.switchTab('archive'));

        // Поиск артикула (из вашего scripts.js)
        const checkArticle = document.getElementById('article');
        checkArticle.addEventListener('input', async () => {
            await this.checkArticle();
        });
    }

    setupSorting() {
        const headers = document.querySelectorAll('.data-table th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.sort;
                if (this.sortField === field) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortField = field;
                    this.sortDirection = 'asc';
                }
                this.sortPositions();
                this.renderTable();
                this.updateSortIndicators();
            });
        });
    }

    updateSortIndicators() {
        const headers = document.querySelectorAll('.data-table th[data-sort]');
        headers.forEach(header => {
            const icon = header.querySelector('i') || document.createElement('i');
            icon.className = 'fas';
            
            if (header.dataset.sort === this.sortField) {
                icon.className = this.sortDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
            } else {
                icon.className = 'fas fa-sort';
            }
            
            if (!header.querySelector('i')) {
                header.appendChild(icon);
            }
        });
    }

    async searchPositions() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            this.showNotification('Введите поисковый запрос', 'warning');
            return;
        }

        try {
            const response = await this.fetchWithCSRF('/sahr/sahr_find/', {
                method: 'POST',
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error('Ошибка поиска');

            const results = await response.json();
            this.displaySearchResults(results);
        } catch (error) {
            console.error('Ошибка поиска:', error);
            this.showNotification('Ошибка при поиске', 'error');
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div class="text-center" style="padding: 1rem; color: var(--text-muted);">Ничего не найдено</div>';
            return;
        }

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <div class="result-article">${result.article || 'Без артикула'}</div>
                <div class="result-details">
                    <span>${result.party || 'Без партии'}</span>
                    <span>${result.address || 'Без адреса'}</span>
                    <span>${result.quantity || 0} ${result.base_unit || ''}</span>
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.highlightTableRow(result.id);
                document.getElementById('searchInput').value = '';
                container.innerHTML = '';
            });
            
            container.appendChild(item);
        });
    }

    highlightTableRow(id) {
        const rows = document.querySelectorAll('#tableBody tr');
        rows.forEach(row => row.classList.remove('highlighted'));
        
        const targetRow = document.querySelector(`#tableBody tr[data-id="${id}"]`);
        if (targetRow) {
            targetRow.classList.add('highlighted');
            targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            setTimeout(() => {
                targetRow.classList.remove('highlighted');
            }, 3000);
        }
    }

    async loadAllPositions() {
        try {
            const response = await this.fetchWithCSRF('/sahr/all_positions/');
            if (!response.ok) throw new Error('Ошибка загрузки данных');
            
            this.allPositions = await response.json();
            this.filteredPositions = [...this.allPositions];
            this.totalPositions = this.allPositions.length;
            this.inBasePositions = this.allPositions.filter(p => p.index_remains === 1).length;
            
            this.sortPositions();
            this.renderTable();
        } catch (error) {
            console.error('Ошибка загрузки позиций:', error);
            this.showNotification('Ошибка загрузки данных', 'error');
        }
    }

    sortPositions() {
        this.filteredPositions.sort((a, b) => {
            let aValue = a[this.sortField];
            let bValue = b[this.sortField];
            
            if (typeof aValue === 'string' && typeof bValue === 'string') {
                return this.sortDirection === 'asc' 
                    ? aValue.localeCompare(bValue)
                    : bValue.localeCompare(aValue);
            }
            
            if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
            if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }

    filterTable(query) {
        if (!query) {
            this.filteredPositions = [...this.allPositions];
        } else {
            const lowerQuery = query.toLowerCase();
            this.filteredPositions = this.allPositions.filter(position => {
                return Object.values(position).some(value => 
                    value && value.toString().toLowerCase().includes(lowerQuery)
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

    renderTable() {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';

        const startIndex = (this.currentPage - 1) * this.rowsPerPage;
        const endIndex = startIndex + this.rowsPerPage;
        const pageData = this.filteredPositions.slice(startIndex, endIndex);

        pageData.forEach(position => {
            const row = document.createElement('tr');
            row.dataset.id = position.id;
            
            const createdDate = position.created_at 
                ? new Date(position.created_at).toLocaleDateString('ru-RU')
                : '—';
            
            const statusBadge = position.index_remains === 1
                ? '<span class="status-badge status-in-base"><i class="fas fa-check"></i> В базе</span>'
                : '<span class="status-badge status-not-in-base"><i class="fas fa-times"></i> Нет в базе</span>';
            
            row.innerHTML = `
                <td>${position.id}</td>
                <td class="text-truncate">${position.article || '—'}</td>
                <td class="text-truncate" title="${position.title || ''}">${position.title || '—'}</td>
                <td>${position.party || '—'}</td>
                <td>${position.address || '—'}</td>
                <td class="text-center">${position.quantity || 0}</td>
                <td class="text-center">${position.base_unit || '—'}</td>
                <td>${statusBadge}</td>
                <td>${createdDate}</td>
                <td class="text-truncate" title="${position.note || ''}">${position.note || '—'}</td>
                <td class="actions-cell">
                    <button class="action-btn edit" onclick="app.editPosition(${position.id})" title="Редактировать">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn history" onclick="app.showHistory(${position.id})" title="История изменений">
                        <i class="fas fa-history"></i>
                    </button>
                    <button class="action-btn delete" onclick="app.confirmDelete(${position.id})" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });

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

    updateStats() {
        document.getElementById('totalPositions').textContent = this.totalPositions;
        document.getElementById('inBasePositions').textContent = this.inBasePositions;
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        const originalHtml = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обновление...';
        refreshBtn.disabled = true;

        await this.loadAllPositions();
        this.updateStats();

        refreshBtn.innerHTML = originalHtml;
        refreshBtn.disabled = false;
        this.showNotification('Данные обновлены', 'success');
    }

    async checkArticle() {
    const articleInput = document.getElementById('article');
    const loader = document.getElementById('articleLoader');
    const titleInput = document.getElementById('title');
    const partySelect = document.getElementById('party');
    const hiddenIdInput = document.getElementById('hiddenId'); // Обновлено
    const hiddenBaseUnitInput = document.getElementById('hiddenBaseUnit'); // Обновлено
    const enteredArticle = articleInput.value.trim();

    if (!enteredArticle) {
        titleInput.value = '';
        partySelect.innerHTML = '<option value="">Выберите партию...</option>';
        hiddenIdInput.value = ''; // Очищаем
        hiddenBaseUnitInput.value = ''; // Очищаем
        return;
    }

    loader.style.display = 'block';

    try {
        const response = await fetch(`/sahr/check-article_form/${enteredArticle}/`);
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Товар не найден');
            } else {
                throw new Error(`HTTP error ${response.status}`);
            }
        }

        const data = await response.json();
        console.log('Получены данные:', data);

        if (data.error) {
            titleInput.value = data.error;
            titleInput.classList.add('error-text');
            partySelect.innerHTML = '<option value="">Нет доступных партий</option>';
            hiddenIdInput.value = '';
            hiddenBaseUnitInput.value = '';
            this.showNotification('Товар не найден в базе', 'warning');
        } else {
            // Заполняем поля формы
            titleInput.value = data.title;
            titleInput.classList.remove('error-text');
            
            // Очищаем и заполняем список партий
            partySelect.innerHTML = '<option value="">Выберите партию...</option>';
            if (data.party && typeof data.party === 'object') {
                Object.values(data.party).forEach(party => {
                    if (party && party.trim()) {
                        const option = document.createElement('option');
                        option.value = party;
                        option.textContent = party;
                        partySelect.appendChild(option);
                    }
                });
            }

            // Заполняем скрытые поля
            if (data.id) {
                hiddenIdInput.value = data.id;
                console.log('ID установлен:', data.id);
            }
            if (data.base_unit) {
                hiddenBaseUnitInput.value = data.base_unit;
                console.log('Ед. изм. установлена:', data.base_unit);
            }

            // Если есть только одна партия - выбираем её автоматически
            if (partySelect.options.length === 2) { // 1 опция + заголовок
                partySelect.selectedIndex = 1;
            }

            this.showNotification('Товар найден', 'success');
        }
    } catch (error) {
        console.error('Ошибка при проверке артикула:', error);
        titleInput.value = 'Ошибка при проверке артикула';
        titleInput.classList.add('error-text');
        partySelect.innerHTML = '<option value="">Ошибка загрузки</option>';
        hiddenIdInput.value = '';
        hiddenBaseUnitInput.value = '';
        
        if (error.message === 'Товар не найден') {
            this.showNotification('Товар не найден в базе данных', 'warning');
        } else {
            this.showNotification('Ошибка при проверке артикула', 'error');
        }
    } finally {
        loader.style.display = 'none';
    }
}

    editPosition(id) {
        const position = this.allPositions.find(p => p.id === id);
        if (!position) return;

        this.editingId = id;
        document.getElementById('editId').value = id;
        document.getElementById('editAddress').value = position.address || '';
        document.getElementById('editQuantity').value = position.quantity || '';
        document.getElementById('editNote').value = position.note || '';

        document.getElementById('editModal').classList.add('active');
    }

    closeEditModal() {
        document.getElementById('editModal').classList.remove('active');
        this.editingId = null;
    }

    async saveEdit() {
        const formData = new FormData(document.getElementById('editForm'));

        try {
            const response = await this.fetchWithCSRF(`/sahr/edit_position/${this.editingId}/`, {
                method: 'PUT',
                body: formData
            });

            if (response.ok) {
                this.showNotification('Позиция успешно обновлена', 'success');
                this.closeEditModal();
                await this.refreshData();
            } else {
                this.showNotification('Ошибка при обновлении', 'error');
            }
        } catch (error) {
            console.error('Ошибка при обновлении:', error);
            this.showNotification('Ошибка при обновлении позиции', 'error');
        }
    }

    async showHistory(id) {
        try {
            const response = await this.fetchWithCSRF(`/sahr/history/${id}/`);
            if (!response.ok) throw new Error('Ошибка загрузки истории');

            const data = await response.json();
            this.displayHistory(data.data, data.related_count);
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            this.showNotification('Ошибка загрузки истории', 'error');
        }
    }

    displayHistory(history, count) {
        const container = document.getElementById('historyList');
        container.innerHTML = '';

        if (history.length === 0) {
            container.innerHTML = '<div class="text-center" style="padding: 1rem; color: var(--text-muted);">История изменений отсутствует</div>';
        } else {
            history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                
                const date = new Date(item.created_at).toLocaleString('ru-RU');
                
                historyItem.innerHTML = `
                    <div class="history-meta">
                        <span>${item.user || 'Система'}</span>
                        <span>${date}</span>
                    </div>
                    <div class="history-changes">${item.changes || 'Изменения не указаны'}</div>
                `;
                
                container.appendChild(historyItem);
            });
        }

        document.getElementById('historyModal').classList.add('active');
    }

    closeHistoryModal() {
        document.getElementById('historyModal').classList.remove('active');
    }

    confirmDelete(id) {
        this.deletingId = id;
        document.getElementById('deleteModal').classList.add('active');
    }

    closeDeleteModal() {
        document.getElementById('deleteModal').classList.remove('active');
        this.deletingId = null;
    }

    async confirmDelete() {
        if (!this.deletingId) return;

        try {
            const response = await this.fetchWithCSRF(`/sahr/remove_position/${this.deletingId}/`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Позиция успешно удалена', 'success');
                this.closeDeleteModal();
                await this.refreshData();
            } else {
                this.showNotification('Ошибка при удалении', 'error');
            }
        } catch (error) {
            console.error('Ошибка при удалении:', error);
            this.showNotification('Ошибка при удалении позиции', 'error');
        }
    }

    async downloadBackup() {
        try {
            const response = await fetch('/sahr/backup/');
            if (!response.ok) throw new Error('Ошибка создания резервной копии');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `CAXP_${new Date().toLocaleDateString('ru-RU').replace(/\./g, '-')}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showNotification('Резервная копия скачана', 'success');
        } catch (error) {
            console.error('Ошибка скачивания:', error);
            this.showNotification('Ошибка скачивания резервной копии', 'error');
        }
    }

    switchTab(tab) {
        const mainTabBtn = document.getElementById('mainTabBtn');
        const archiveTabBtn = document.getElementById('archiveTabBtn');
        const contentTitle = document.getElementById('contentTitle');

        if (tab === 'main') {
            mainTabBtn.classList.add('active');
            archiveTabBtn.classList.remove('active');
            contentTitle.textContent = 'Основная таблица позиций';
            this.loadAllPositions();
        } else if (tab === 'archive') {
            mainTabBtn.classList.remove('active');
            archiveTabBtn.classList.add('active');
            contentTitle.textContent = 'Архив удаленных позиций';
            this.loadArchive();
        }
    }

    async loadArchive() {
        try {
            const response = await this.fetchWithCSRF('/sahr/archive_remove_positions/');
            if (!response.ok) throw new Error('Ошибка загрузки архива');
            
            this.allPositions = await response.json();
            this.filteredPositions = [...this.allPositions];
            this.sortPositions();
            this.renderTable();
        } catch (error) {
            console.error('Ошибка загрузки архива:', error);
            this.showNotification('Ошибка загрузки архива', 'error');
        }
    }
}

// Инициализация приложения
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SahrApp();
});

// Экспорт функций для глобального использования
window.app = app;
window.submitArticleForm = () => app.submitArticleForm();
window.closeEditModal = () => app.closeEditModal();
window.saveEdit = () => app.saveEdit();
window.closeHistoryModal = () => app.closeHistoryModal();
window.closeDeleteModal = () => app.closeDeleteModal();
window.confirmDelete = () => app.confirmDelete();