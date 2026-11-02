class SahrApp {
    constructor() {
        this.currentPage = 1;
        this.rowsPerPage = 25;
        this.sortField = 'id';
        this.sortDirection = 'desc';
        this.allPositions = [];
        this.filteredPositions = [];
        this.totalPositions = 0;
        this.inBasePositions = 0;
        this.editingId = null;
        this.deletingId = null;
        this.positionsWithHistory = new Set();
        
        this.init();
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
            console.error('Ошибка форматирования даты:', error);
            return '—';
        }
    }

    convertToLocalTime(utcDateString) {
        if (!utcDateString) return null;
        try {
            const date = new Date(utcDateString);
            return new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
        } catch (error) {
            console.error('Ошибка преобразования времени:', error);
            return null;
        }
    }

    async init() {
        this.setupEventListeners();
        await this.loadAllPositions();
        this.updateStats();
        this.setupSorting();
    }

    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }

    async fetchWithCSRF(url, options = {}) {
        const csrfToken = this.getCSRFToken();
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options });
    }

    async fetchFormData(url, formData) {
        const csrfToken = this.getCSRFToken();
        
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
    }

    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        if (!notifications) return;
        
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
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchPositions());
        }
        
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.searchPositions();
            });
        }

        // Пагинация
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
        
        const rowsPerPage = document.getElementById('rowsPerPage');
        if (rowsPerPage) {
            rowsPerPage.addEventListener('change', (e) => {
                this.rowsPerPage = parseInt(e.target.value);
                this.currentPage = 1;
                this.renderTable();
            });
        }

        // Кнопки пагинации
        const firstPage = document.getElementById('firstPage');
        if (firstPage) firstPage.addEventListener('click', () => this.goToPage(1));
        
        const prevPage = document.getElementById('prevPage');
        if (prevPage) prevPage.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        
        const nextPage = document.getElementById('nextPage');
        if (nextPage) nextPage.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        
        const lastPage = document.getElementById('lastPage');
        if (lastPage) lastPage.addEventListener('click', () => this.goToPage(this.getTotalPages()));

        // Фильтр таблицы
        const tableFilter = document.getElementById('tableFilter');
        if (tableFilter) {
            tableFilter.removeEventListener('input', this.filterTable.bind(this));
            tableFilter.addEventListener('input', (e) => {
                this.filterTable(e.target.value);
            });
            tableFilter.value = '';
        }

        // Резервное копирование
        const backupBtn = document.getElementById('backupBtn');
        if (backupBtn) {
            backupBtn.addEventListener('click', () => this.downloadBackup());
        }

        // Поиск артикула
        const checkArticle = document.getElementById('article');
        if (checkArticle) {
            checkArticle.addEventListener('input', async () => {
                await this.checkArticle();
            });
        }

        // Отправка формы добавления позиции
        const articleForm = document.getElementById('articleForm');
        if (articleForm) {
            articleForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitArticleForm();
            });
        }

        // Модальное окно редактирования
        const editPartySelect = document.getElementById('editParty');
        if (editPartySelect) {
            editPartySelect.addEventListener('change', (e) => {
                const article = document.getElementById('editId')?.value;
                if (article && e.target.value) {
                    this.getArticleParties(article);
                }
            });
        }

        // === МАССОВАЯ ЗАМЕНА АДРЕСА ===
        const bulkReplaceBtn = document.getElementById('bulkReplaceBtn');
        if (bulkReplaceBtn) {
            bulkReplaceBtn.addEventListener('click', () => this.openBulkReplaceModal());
        }

        const bulkOldAddress = document.getElementById('bulkOldAddress');
        if (bulkOldAddress) {
            let previewTimer = null;
            bulkOldAddress.addEventListener('input', (e) => {
                clearTimeout(previewTimer);
                const value = e.target.value.trim();
                previewTimer = setTimeout(() => this.previewBulkReplace(value), 300);
            });
        }

        const bulkReplaceConfirmBtn = document.getElementById('bulkReplaceConfirmBtn');
        if (bulkReplaceConfirmBtn) {
            bulkReplaceConfirmBtn.addEventListener('click', () => this.submitBulkReplace());
        }

        // === ЗАЩИТА ОТ КИРИЛЛИЦЫ В АДРЕСАХ ===
        const addressInputs = [
            document.getElementById('address'),        // Добавление
            document.getElementById('editAddress'),    // Редактирование
            document.getElementById('bulkNewAddress')  // Новый адрес (массовая замена)
        ];

        addressInputs.forEach(input => {
            if (input) {
                input.addEventListener('input', (e) => {
                    const hasCyrillic = /[а-яё]/i.test(e.target.value);
                    if (hasCyrillic) {
                        e.target.value = e.target.value.replace(/[а-яё]/gi, '');
                        this.showNotification('В адресах запрещены русские буквы. Используйте латиницу.', 'warning');
                    }
                });
            }
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
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;
        
        const query = searchInput.value.trim();
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
        if (!container) return;
        
        container.innerHTML = '';

        if (!results || results.length === 0) {
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
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.highlightTableRow(result.id);
                const searchInput = document.getElementById('searchInput');
                if (searchInput) searchInput.value = '';
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
            this.allPositions.sort((a, b) => b.id - a.id);
            this.filteredPositions = [...this.allPositions];
            this.totalPositions = this.allPositions.length;
            this.inBasePositions = this.allPositions.filter(p => p.index_remains === 1).length;
            
            const tableFilter = document.getElementById('tableFilter');
            if (tableFilter) tableFilter.value = '';
            
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
                return Object.entries(position).some(([key, value]) => {
                    if (key === 'id' || key === 'index_remains') return false;
                    
                    if (value !== null && value !== undefined) {
                        return value.toString().toLowerCase().includes(lowerQuery);
                    }
                    return false;
                });
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
        if (!tbody) return;
        
        tbody.innerHTML = '';
    
        const startIndex = (this.currentPage - 1) * this.rowsPerPage;
        const endIndex = startIndex + this.rowsPerPage;
        const pageData = this.filteredPositions.slice(startIndex, endIndex);
    
        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center" style="padding: 3rem;">
                        <div style="color: var(--text-muted);">
                            <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                            <p>Нет данных для отображения</p>
                            ${this.allPositions.length > 0 ? '<p class="text-small">Попробуйте изменить поисковый запрос</p>' : ''}
                        </div>
                    </td>
                </tr>
            `;
            this.updatePagination();
            return;
        }
    
        pageData.forEach(position => {
            const row = document.createElement('tr');
            row.dataset.id = position.id;
            row.dataset.article = position.article;
            
            const formattedDate = this.formatDateTime(position.date);
            
            let statusBadge = '';
            if (position.index_remains === 1) {
                statusBadge = `
                    <span class="status-badge status-in-base clickable-status" 
                          title="Кликните для проверки остатков" 
                          data-article="${position.article}">
                        <i class="fas fa-check"></i> В базе
                    </span>
                `;
            } else if (position.index_remains === 0) {
                statusBadge = `
                    <span class="status-badge status-not-in-base clickable-status" 
                          title="Кликните для проверки остатков" 
                          data-article="${position.article}">
                        <i class="fas fa-times"></i> Нет в базе
                    </span>
                `;
            } else {
                statusBadge = `
                    <span class="status-badge status-unknown clickable-status" 
                          title="Кликните для проверки остатков" 
                          data-article="${position.article}">
                        <i class="fas fa-question"></i> Не проверен
                    </span>
                `;
            }
            
            const commentText = position.comment || position.note || '';
            
            row.innerHTML = `
                <td hidden>${position.id}</td>
                <td class="text-truncate" title="${position.article || ''}">${position.article || '—'}</td>
                <td class="text-truncate" title="${position.party || ''}">${position.party || '—'}</td>
                <td class="text-truncate" title="${position.title || ''}">${position.title || '—'}</td>
                <td>${position.address || '—'}</td>
                <td class="text-center">${position.base_unit || '—'}</td>
                <td class="text-truncate">${formattedDate}</td>
                <td class="text-truncate" title="${commentText}">${commentText || '—'}</td>
                <td>${statusBadge}</td>
                <td class="actions-cell">
                    <div class="action-btn edit" data-id="${position.id}">
                        <img src="/static/comers/icons/icon_edit.png" title="Редактировать">
                    </div>
                    <div class="edit_invoice_button edit_status_button" data-id="${position.id}">
                        <img src="/static/comers/icons/icon_status.png" title="История изменений">
                    </div>
                    <div class="edit_invoice_button delete_button" data-id="${position.id}">
                        <img src="/static/comers/icons/icon_delete.png" title="Удалить">
                    </div>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    
        this.addActionHandlers();
        this.updatePagination();
    }

    addActionHandlers() {
        const editButtons = document.querySelectorAll('.action-btn.edit');
        editButtons.forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(e.currentTarget.dataset.id);
                this.editPosition(id);
            });
        });
    
        const historyButtons = document.querySelectorAll('.edit_invoice_button.edit_status_button');
        historyButtons.forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(e.currentTarget.dataset.id);
                this.showHistory(id);
            });
        });
    
        const deleteButtons = document.querySelectorAll('.edit_invoice_button.delete_button');
        deleteButtons.forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                const id = parseInt(newButton.dataset.id);
                this.confirmDelete(id);
            });
        });

        const statusBadges = document.querySelectorAll('.clickable-status');
        statusBadges.forEach(badge => {
            const newBadge = badge.cloneNode(true);
            badge.parentNode.replaceChild(newBadge, badge);
            
            newBadge.addEventListener('click', (e) => {
                e.stopPropagation();
                const article = e.currentTarget.dataset.article;
                this.checkArticleStock(article);
            });
        });
    }

    updatePagination() {
        const totalPages = this.getTotalPages();
        const totalItems = this.filteredPositions.length;
        const startItem = totalItems > 0 ? (this.currentPage - 1) * this.rowsPerPage + 1 : 0;
        const endItem = Math.min(this.currentPage * this.rowsPerPage, totalItems);

        const paginationInfo = document.getElementById('paginationInfo');
        if (paginationInfo) {
            paginationInfo.textContent = `Показано ${startItem}-${endItem} из ${totalItems} записей`;
        }

        const pageNumbers = document.getElementById('pageNumbers');
        if (pageNumbers) {
            pageNumbers.textContent = `${this.currentPage} из ${totalPages}`;
        }

        const firstPage = document.getElementById('firstPage');
        const prevPage = document.getElementById('prevPage');
        const nextPage = document.getElementById('nextPage');
        const lastPage = document.getElementById('lastPage');

        if (firstPage) {
            firstPage.disabled = this.currentPage === 1;
            firstPage.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 12L4 8L8 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 12L8 8L12 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
        if (prevPage) {
            prevPage.disabled = this.currentPage === 1;
            prevPage.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
        if (nextPage) {
            nextPage.disabled = this.currentPage === totalPages;
            nextPage.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
        if (lastPage) {
            lastPage.disabled = this.currentPage === totalPages;
            lastPage.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M4 12L8 8L4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 12L12 8L8 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
    }

    async checkArticleStock(article) {
        if (!article) {
            this.showNotification('Артикул не найден', 'warning');
            return;
        }

        try {
            const loader = this.createStatusLoader();
            document.querySelectorAll(`.clickable-status[data-article="${article}"]`).forEach(badge => {
                badge.appendChild(loader);
            });

            const response = await fetch(`/finder/get_details/article_id/${article}/`);
            if (!response.ok) throw new Error('Ошибка проверки остатков');

            const data = await response.json();

            loader.remove();

            const stockInfo = data.total_sum_any_projects || 0;
            const unit = data.base_unit || 'шт';
            
            this.showNotification(`Остаток по артикулу ${article}: ${stockInfo} ${unit}`, 'success');

            if (stockInfo > 0) {
                this.updateStockStatus(article, stockInfo, unit);
            }

        } catch (error) {
            console.error('Ошибка проверки остатков:', error);
            this.showNotification('Ошибка при проверке остатков', 'error');
        }
    }

    createStatusLoader() {
        const loader = document.createElement('span');
        loader.className = 'status-loader';
        loader.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-left: 5px;"></i>';
        return loader;
    }

    updateStockStatus(article, stock, unit) {
        const rows = document.querySelectorAll(`tr[data-article="${article}"]`);
        rows.forEach(row => {
            const statusCell = row.querySelector('.clickable-status');
            if (statusCell) {
                statusCell.title = `Остаток: ${stock} ${unit}`;
                
                if (stock > 0) {
                    const icon = statusCell.querySelector('i');
                    if (icon) {
                        statusCell.innerHTML = `<i class="fas fa-check"></i> ${stock} ${unit}`;
                    }
                }
            }
        });
    }

    updateStats() {
        const totalPositionsEl = document.getElementById('totalPositions');
        const inBasePositionsEl = document.getElementById('inBasePositions');
        
        if (totalPositionsEl) totalPositionsEl.textContent = this.totalPositions;
        if (inBasePositionsEl) inBasePositionsEl.textContent = this.inBasePositions;
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (!refreshBtn) return;
        
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
        
        if (!articleInput || !titleInput || !partySelect) {
            console.error('Не найдены элементы формы');
            return;
        }
        
        const enteredArticle = articleInput.value.trim();

        if (!enteredArticle) {
            titleInput.value = '';
            partySelect.innerHTML = '<option value="">Выберите партию...</option>';
            return;
        }

        if (loader) loader.style.display = 'block';

        try {
            const response = await fetch(`/sahr/check-article_form/${enteredArticle}/`);
            if (!response.ok) throw new Error('Ошибка проверки артикула');

            const data = await response.json();

            if (data.error) {
                titleInput.value = data.error;
                partySelect.innerHTML = '<option value="">Нет доступных партий</option>';
                this.showNotification('Товар не найден в базе', 'warning');
            } else {
                titleInput.value = data.title;
                
                partySelect.innerHTML = '<option value="">Выберите партию...</option>';
                if (data.party && typeof data.party === 'object') {
                    Object.values(data.party).forEach(party => {
                        const option = document.createElement('option');
                        option.value = party;
                        option.textContent = party;
                        partySelect.appendChild(option);
                    });
                }

                this.addHiddenFields(data);

                this.showNotification('Товар найден', 'success');
            }
        } catch (error) {
            console.error('Ошибка при проверке артикула:', error);
            titleInput.value = 'Ошибка при проверке';
            this.showNotification('Ошибка при проверке артикула', 'error');
        } finally {
            if (loader) loader.style.display = 'none';
        }
    }

    addHiddenFields(data) {
        const form = document.getElementById('articleForm');
        if (!form) return;

        const existingHiddenFields = form.querySelectorAll('input[type="hidden"]');
        existingHiddenFields.forEach(field => {
            if (field.name === 'id' || field.name === 'base_unit' || field.name === 'title' || field.name === 'article') {
                field.remove();
            }
        });

        const idField = document.createElement('input');
        idField.type = 'hidden';
        idField.name = 'id';
        idField.value = data.id || '';
        form.appendChild(idField);

        const unitField = document.createElement('input');
        unitField.type = 'hidden';
        unitField.name = 'base_unit';
        unitField.value = data.base_unit || '';
        form.appendChild(unitField);

        const titleField = document.createElement('input');
        titleField.type = 'hidden';
        titleField.name = 'title';
        titleField.value = data.title || '';
        form.appendChild(titleField);

        const articleField = document.createElement('input');
        articleField.type = 'hidden';
        articleField.name = 'article';
        articleField.value = data.article || '';
        form.appendChild(articleField);
    }

    async submitArticleForm() {
        const form = document.getElementById('articleForm');
        if (!form) {
            console.error('Форма не найдена');
            return;
        }
    
        const formData = new FormData(form);
    
        const requiredFields = ['article', 'party', 'address'];
        const missingFields = [];
        
        requiredFields.forEach(field => {
            if (!formData.get(field)) {
                missingFields.push(field);
            }
        });
    
        if (missingFields.length > 0) {
            this.showNotification(`Заполните обязательные поля: ${missingFields.join(', ')}`, 'warning');
            return;
        }
    
        const noteField = document.getElementById('note');
        if (noteField && noteField.value) {
            formData.append('comment', noteField.value);
        }
    
        try {
            const response = await this.fetchFormData('/sahr/add_position/', formData);
            
            const result = await response.json();
    
            if (response.ok) {
                this.showNotification('Позиция успешно добавлена!', 'success');
                
                form.reset();
                
                const titleInput = document.getElementById('title');
                const partySelect = document.getElementById('party');
                if (titleInput) titleInput.value = '';
                if (partySelect) partySelect.innerHTML = '<option value="">Выберите партию...</option>';
                
                await this.refreshData();
            } else {
                this.showNotification(`Ошибка: ${result.error || 'Неизвестная ошибка'}`, 'error');
            }
        } catch (error) {
            console.error('Ошибка при добавлении:', error);
            this.showNotification('Ошибка при добавлении позиции', 'error');
        }
    }

    async getArticleParties(article) {
        if (!article) return;

        try {
            const response = await fetch(`/finder/get_details/article_id/${article}/`);
            if (!response.ok) throw new Error('Ошибка загрузки партий');

            const data = await response.json();
            
            const partySelect = document.getElementById('editParty');
            if (partySelect && data.party && Array.isArray(data.party)) {
                const currentValue = partySelect.value;
                
                partySelect.innerHTML = '<option value="">Выберите партию...</option>';
                data.party.forEach(party => {
                    const option = document.createElement('option');
                    option.value = party;
                    option.textContent = party;
                    partySelect.appendChild(option);
                });
                
                if (currentValue) {
                    partySelect.value = currentValue;
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки партий:', error);
        }
    }

    editPosition(id) {
        const position = this.allPositions.find(p => p.id === id);
        if (!position) return;
    
        this.editingId = id;
        
        const editModal = document.getElementById('editModal');
        const editId = document.getElementById('editId');
        const editAddress = document.getElementById('editAddress');
        const editComment = document.getElementById('editComment');
        const editParty = document.getElementById('editParty');
        const editArticle = document.getElementById('editArticle');
        const editTitle = document.getElementById('editTitle');
        
        const editArticleDisplay = document.getElementById('editArticleDisplay');
        const editTitleDisplay = document.getElementById('editTitleDisplay');
        const editUnitDisplay = document.getElementById('editUnitDisplay');
        const editBaseUnit = document.getElementById('editBaseUnit');
        
        if (editId) editId.value = id;
        if (editAddress) editAddress.value = position.address || '';
        if (editComment) editComment.value = position.comment || position.note || '';
        if (editParty) editParty.value = position.party || '';
        
        if (editArticle) editArticle.value = position.article || '';
        if (editTitle) editTitle.value = position.title || '';
        
        if (editArticleDisplay) {
            editArticleDisplay.textContent = position.article || '—';
            editArticleDisplay.style.display = 'block';
        }
        
        if (editTitleDisplay) {
            editTitleDisplay.textContent = position.title || '—';
            editTitleDisplay.style.display = 'block';
        }
        
        if (editUnitDisplay) {
            editUnitDisplay.textContent = position.base_unit || 'шт';
            editUnitDisplay.style.display = 'block';
        }
        
        if (editBaseUnit) editBaseUnit.value = position.base_unit || '';
        
        if (position.article) {
            this.getArticleParties(position.article);
        }
    
        if (editModal) editModal.classList.add('active');
    }

    closeEditModal() {
        const editModal = document.getElementById('editModal');
        if (editModal) editModal.classList.remove('active');
        this.editingId = null;
    }

    async saveEdit() {
        const form = document.getElementById('editForm');
        if (!form || !this.editingId) return;
    
        const formData = new FormData(form);
        const data = {
            address: formData.get('address') || '',
            comment: formData.get('comment') || '',
            party: formData.get('party') || ''
        };
    
        Object.keys(data).forEach(key => {
            if (data[key] === '' || data[key] === null) {
                delete data[key];
            }
        });
    
        try {
            const response = await this.fetchWithCSRF(`/sahr/edit_position/${this.editingId}/`, {
                method: 'PATCH',
                body: JSON.stringify(data)
            });
    
            const result = await response.json();
    
            if (response.ok) {
                this.showNotification('Позиция успешно обновлена', 'success');
                this.closeEditModal();
                await this.refreshData();
            } else {
                this.showNotification(`Ошибка при обновлении: ${result.error || result.address?.[0] || 'Неизвестная ошибка'}`, 'error');
            }
        } catch (error) {
            console.error('Ошибка при обновлении:', error);
            this.showNotification('Ошибка при обновлении позиции', 'error');
        }
    }

    confirmDelete(id) {
        this.deletingId = id;
        const deleteModal = document.getElementById('deleteModal');
        if (deleteModal) deleteModal.classList.add('active');
    }

    closeDeleteModal() {
        const deleteModal = document.getElementById('deleteModal');
        if (deleteModal) deleteModal.classList.remove('active');
        this.deletingId = null;
    }

    async performDelete() {
        if (!this.deletingId) {
            console.error('Нет ID для удаления');
            return;
        }
        
        const id = this.deletingId;
        
        try {
            const response = await this.fetchWithCSRF(`/sahr/remove_position/${id}/`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showNotification('Позиция успешно удалена', 'success');
                this.closeDeleteModal();
                
                this.allPositions = this.allPositions.filter(p => p.id !== id);
                this.filteredPositions = this.filteredPositions.filter(p => p.id !== id);
                
                this.positionsWithHistory.delete(id);
                
                this.renderTable();
                this.updateStats();
                
            } else {
                let errorMessage = `Ошибка удаления: ${response.status}`;
                if (response.status === 403) errorMessage = 'Доступ запрещен.';
                if (response.status === 404) errorMessage = 'Позиция не найдена.';
                
                this.showNotification(errorMessage, 'error');
                this.closeDeleteModal();
            }
            
        } catch (error) {
            console.error('Исключение при удалении:', error);
            this.showNotification(`Ошибка сети: ${error.message}`, 'error');
            this.closeDeleteModal();
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

    async showHistory(id) {
        try {
            const response = await this.fetchWithCSRF(`/sahr/history/${id}/`);
            if (!response.ok) throw new Error('Ошибка загрузки истории');
    
            const data = await response.json();
            this.displayHistory(data.data, data.related_count, id);
            
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            this.showNotification('Ошибка загрузки истории изменений', 'error');
        }
    }
    
    displayHistory(history, count, positionId) {
        const container = document.getElementById('historyList');
        if (!container) return;
        
        container.innerHTML = '';

        const currentPosition = this.allPositions.find(p => p.id === positionId);
        const positionInfo = currentPosition ? 
            `${currentPosition.article} - ${currentPosition.title}` : 
            `Позиция ID: ${positionId}`;

        const header = document.createElement('div');
        header.className = 'history-header';
        header.innerHTML = `
            <h4>История изменений</h4>
            <p class="history-position-info">Позиция: ${positionInfo}</p>
            <p class="history-count">Всего изменений: ${count}</p>
        `;
        container.appendChild(header);

        if (!history || history.length === 0) {
            container.innerHTML += `
                <div class="history-empty text-center" style="padding: 2rem; color: var(--text-muted);">
                    <i class="fas fa-history" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>История изменений отсутствует</p>
                </div>
            `;
            return;
        }

        // Сортируем по дате: СТАРЫЕ СВЕРХУ, НОВЫЕ СНИЗУ
        const sortedHistory = [...history].sort((a, b) => {
            const dateA = new Date(a.date || a.created_at || 0);
            const dateB = new Date(b.date || b.created_at || 0);
            return dateA - dateB;
        });

        sortedHistory.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.style.marginBottom = '15px';

            const itemDate = item.date || item.created_at;
            const dateFormatted = itemDate ? this.formatDateTime(itemDate) : 'Дата не указана';

            // Ищем пометки об изменениях
            let addressBlock = `<div class="history-field"><strong>Адрес:</strong> ${item.address || '—'}</div>`;
            
            // 1. Если это массовая замена (ищем в комментарии)
            if (item.comment && item.comment.includes('[Массовая замена]')) {
                const match = item.comment.match(/\[Массовая замена\]\s*(\S+)\s*→\s*(\S+)/);
                if (match) {
                    addressBlock = `
                        <div class="history-field" style="background:#fff4e5; padding:8px; border-radius:6px; border:1px solid #ffd699;">
                            <strong>Адрес (массовая):</strong>
                            <span style="text-decoration: line-through; color: #a4282a;">${match[1]}</span>
                            <span style="margin: 0 6px;">→</span>
                            <span style="color: #256029; font-weight: 600;">${match[2]}</span>
                        </div>
                    `;
                }
            } 
            // 2. Если это ручное изменение (сигнал добавил маркер [Изменено: ...])
            else if (item.comment && item.comment.includes('[Изменено:')) {
                const match = item.comment.match(/\[Изменено:\s*Адрес:\s*(\S+)\s*→\s*(\S+)\]/);
                if (match) {
                    addressBlock = `
                        <div class="history-field" style="background:#e8f5e9; padding:8px; border-radius:6px; border:1px solid #b7e0b9;">
                            <strong>Адрес:</strong>
                            <span style="text-decoration: line-through; color: #a4282a;">${match[1]}</span>
                            <span style="margin: 0 6px;">→</span>
                            <span style="color: #256029; font-weight: 600;">${match[2]}</span>
                        </div>
                    `;
                }
            }

            // Очищаем комментарий от технических маркеров для вывода
            let displayComment = item.comment || '';
            displayComment = displayComment
                .replace(/\[Массовая замена\][^.]*\./, '')
                .replace(/\[Изменено:[^\]]*\]/, '')
                .trim();

            historyItem.innerHTML = `
                <div class="history-item-header">
                    <span class="history-change-type" style="background:#e9ecef;color:#495057;">Запись от ${dateFormatted}</span>
                </div>
                <div class="history-content">
                    <div class="history-fields">
                        ${item.article ? `<div class="history-field"><strong>Артикул:</strong> ${item.article}</div>` : ''}
                        ${item.party ? `<div class="history-field"><strong>Партия:</strong> ${item.party}</div>` : ''}
                        ${item.title ? `<div class="history-field"><strong>Номенклатура:</strong> ${item.title}</div>` : ''}
                        ${addressBlock}
                        ${displayComment ? `<div class="history-field"><strong>Примечание:</strong> ${displayComment}</div>` : ''}
                    </div>
                </div>
            `;

            container.appendChild(historyItem);
        });

        // В самом низу добавляем блок "Текущее состояние"
        if (currentPosition) {
            const currentItem = document.createElement('div');
            currentItem.className = 'history-item';
            currentItem.style.border = '2px solid #007bff';
            currentItem.innerHTML = `
                <div class="history-item-header">
                    <span class="history-change-type" style="background:#007bff;color:#fff;">Текущее состояние (сейчас)</span>
                </div>
                <div class="history-content">
                    <div class="history-fields">
                        <div class="history-field"><strong>Артикул:</strong> ${currentPosition.article || '—'}</div>
                        <div class="history-field"><strong>Партия:</strong> ${currentPosition.party || '—'}</div>
                        <div class="history-field"><strong>Номенклатура:</strong> ${currentPosition.title || '—'}</div>
                        <div class="history-field" style="background:#e6f2ff; padding:8px; border-radius:6px;">
                            <strong>Адрес:</strong>
                            <span style="color: #0056b3; font-weight: 600;">${currentPosition.address || '—'}</span>
                        </div>
                        <div class="history-field"><strong>Примечание:</strong> ${currentPosition.comment || currentPosition.note || '—'}</div>
                    </div>
                </div>
            `;
            container.appendChild(currentItem);
        }

        const historyModal = document.getElementById('historyModal');
        if (historyModal) historyModal.classList.add('active');
    }

    closeHistoryModal() {
        const historyModal = document.getElementById('historyModal');
        if (historyModal) historyModal.classList.remove('active');
    }

    // =====================================================
    // МАССОВАЯ ЗАМЕНА АДРЕСА
    // =====================================================

    isAddressMatch(addressInDb, userInput) {
        if (!addressInDb || !userInput) return false;
        
        // Простое сравнение
        if (addressInDb.toLowerCase() === userInput.toLowerCase()) return true;

        // Карта похожих символов
        const layoutMap = {
            'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н', 'k': 'к', 
            'm': 'м', 'o': 'о', 'p': 'р', 't': 'т', 'x': 'х', 'y': 'у'
        };
        
        const normalize = (str) => {
            return str.toLowerCase().split('').map(char => layoutMap[char] || char).join('');
        };

        return normalize(addressInDb) === normalize(userInput);
    }

    openBulkReplaceModal() {
        const form = document.getElementById('bulkReplaceForm');
        if (form) form.reset();

        const preview = document.getElementById('bulkReplacePreview');
        if (preview) {
            preview.className = 'bulk-replace-warning';
            preview.textContent = '';
        }

        const modal = document.getElementById('bulkReplaceModal');
        if (modal) modal.classList.add('active');

        const oldInput = document.getElementById('bulkOldAddress');
        if (oldInput) oldInput.focus();
    }

    closeBulkReplaceModal() {
        const modal = document.getElementById('bulkReplaceModal');
        if (modal) modal.classList.remove('active');
    }

    previewBulkReplace(oldAddress) {
        const preview = document.getElementById('bulkReplacePreview');
        if (!preview) return;

        if (!oldAddress) {
            preview.className = 'bulk-replace-warning';
            preview.textContent = '';
            return;
        }

        const count = this.allPositions.filter(
            p => this.isAddressMatch(p.address, oldAddress)
        ).length;

        preview.classList.add('visible');
        if (count > 0) {
            preview.className = 'bulk-replace-warning visible';
            preview.innerHTML = `Будет перенесено позиций: <b>${count}</b>`;
        } else {
            preview.className = 'bulk-replace-warning visible is-danger';
            preview.textContent = 'Позиции с таким адресом не найдены';
        }
    }

    async submitBulkReplace() {
        const oldInput = document.getElementById('bulkOldAddress');
        const newInput = document.getElementById('bulkNewAddress');
        const confirmBtn = document.getElementById('bulkReplaceConfirmBtn');

        const oldAddress = oldInput ? oldInput.value.trim() : '';
        const newAddress = newInput ? newInput.value.trim() : '';

        if (!oldAddress || !newAddress) {
            this.showNotification('Заполните оба адреса', 'warning');
            return;
        }

        // Проверка на кириллицу в НОВОМ адресе
        if (/[а-яё]/i.test(newAddress)) {
            this.showNotification('Новый адрес содержит русские буквы! Переключите раскладку.', 'error');
            if (newInput) newInput.focus();
            return;
        }

        if (oldAddress.toLowerCase() === newAddress.toLowerCase()) {
            this.showNotification('Адреса совпадают', 'warning');
            return;
        }

        if (!confirm(
            `Заменить адрес "${oldAddress}" на "${newAddress}" у ВСЕХ позиций?\n` +
            `Будут затронуты позиции с обоими вариантами раскладки (RU/EN).\n` +
            `Действие необратимо (кроме истории изменений).`
        )) {
            return;
        }

        const originalHtml = confirmBtn ? confirmBtn.innerHTML : '';
        if (confirmBtn) {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Замена...';
        }

        try {
            const response = await this.fetchWithCSRF('/sahr/bulk_replace_address/', {
                method: 'POST',
                body: JSON.stringify({
                    old_address: oldAddress,
                    new_address: newAddress,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification(data.message, 'success');
                this.closeBulkReplaceModal();
                await this.refreshData();
            } else {
                let msg = data.error || 'Ошибка замены';
                if (data.conflicts && data.conflicts.length) {
                    msg += '\n\nКонфликты:\n' +
                        data.conflicts.map(c => `${c.article} (партия ${c.party})`).join('\n');
                }
                this.showNotification(msg, 'error');
            }
        } catch (error) {
            console.error('Ошибка замены адреса:', error);
            this.showNotification('Ошибка сети при замене адреса', 'error');
        } finally {
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = originalHtml || '<i class="fas fa-check"></i> Заменить адрес';
            }
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

window.closeEditModal = () => {
    if (app && app.closeEditModal) {
        app.closeEditModal();
    }
};

window.saveEdit = () => {
    if (app && app.saveEdit) {
        app.saveEdit();
    }
};

window.closeHistoryModal = () => {
    if (app && app.closeHistoryModal) {
        app.closeHistoryModal();
    }
};

window.closeDeleteModal = () => {
    if (app && app.closeDeleteModal) {
        app.closeDeleteModal();
    } else {
        const deleteModal = document.getElementById('deleteModal');
        if (deleteModal) {
            deleteModal.classList.remove('active');
        }
    }
};

window.confirmDelete = () => {
    if (app && app.performDelete) {
        app.performDelete();
    } else if (app && app.confirmDelete) {
        app.confirmDelete();
    } else {
        console.error('app или методы не найдены');
        alert('Ошибка: приложение не инициализировано');
    }
};

window.submitArticleForm = () => {
    if (app && app.submitArticleForm) {
        app.submitArticleForm();
    }
};

window.openBulkReplaceModal = () => {
    if (app && app.openBulkReplaceModal) app.openBulkReplaceModal();
};

window.closeBulkReplaceModal = () => {
    if (app && app.closeBulkReplaceModal) app.closeBulkReplaceModal();
};

window.submitBulkReplace = () => {
    if (app && app.submitBulkReplace) app.submitBulkReplace();
};