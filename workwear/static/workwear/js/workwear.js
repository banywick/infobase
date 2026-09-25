// Workwear page logic
class WorkwearPage {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 50;
        this.filters = {
            search: '',
            status: '',
            category: '',
            expiration_from: '',
            expiration_to: ''
        };
        this.categories = [];
        this.allEmployees = [];  // кэш сотрудников
        this.selectedEmployeeId = null;
        this.init();
    }
    
    async init() {
        this.bindEvents();
        await this.loadCategories();
        await this.preloadEmployees();  // загружаем сотрудников в кэш
        await this.loadWorkwear();
        this.initEmployeeSearch();  // инициализируем поиск
    }
    
    bindEvents() {
        let searchTimeout;
        
        // Фильтры таблицы
        document.getElementById('searchInput')?.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.currentPage = 1;
                this.loadWorkwear();
            }, 300);
        });
        
        document.getElementById('statusFilter')?.addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('expirationFrom')?.addEventListener('change', (e) => {
            this.filters.expiration_from = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('expirationTo')?.addEventListener('change', (e) => {
            this.filters.expiration_to = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('resetFilters')?.addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            document.getElementById('statusFilter').value = '';
            document.getElementById('categoryFilter').value = '';
            document.getElementById('expirationFrom').value = '';
            document.getElementById('expirationTo').value = '';
            this.filters = { search: '', status: '', category: '', expiration_from: '', expiration_to: '' };
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        // Кнопка сохранения
        document.getElementById('saveWorkwearBtn')?.addEventListener('click', () => {
            this.saveWorkwear();
        });
    }
    
    // ========== Загрузка категорий ==========
    async loadCategories() {
        try {
            const categories = await API.getCategories();
            this.categories = categories;
            
            // Заполняем фильтр категорий
            const filterSelect = document.getElementById('categoryFilter');
            if (filterSelect) {
                categories.forEach(cat => {
                    if (cat.is_active) {
                        const opt = document.createElement('option');
                        opt.value = cat.id;
                        opt.textContent = cat.name;
                        filterSelect.appendChild(opt);
                    }
                });
            }
            
            // Заполняем селект категорий в форме
            const formSelect = document.getElementById('categorySelect');
            if (formSelect) {
                categories.forEach(cat => {
                    if (cat.is_active) {
                        const opt = document.createElement('option');
                        opt.value = cat.id;
                        opt.textContent = cat.name;
                        formSelect.appendChild(opt);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }
    
    // ========== Предзагрузка ВСЕХ сотрудников ==========
    async preloadEmployees() {
        try {
            const response = await fetch('/workwear/api/employees/?page_size=2000');
            const data = await response.json();
            this.allEmployees = data.results || data;
            console.log(`✅ Загружено ${this.allEmployees.length} сотрудников в кэш`);
        } catch (error) {
            console.error('❌ Ошибка предзагрузки сотрудников:', error);
            this.allEmployees = [];
        }
    }
    
    // ========== Инициализация поиска сотрудников ==========
    initEmployeeSearch() {
        const searchInput = document.getElementById('employeeSearch');
        const hiddenInput = document.getElementById('employeeId');
        const suggestionsBox = document.getElementById('employeeSuggestions');
        const selectedInfo = document.getElementById('employeeSelected');
        
        if (!searchInput || !suggestionsBox) {
            console.warn('⚠️ Элементы поиска сотрудников не найдены');
            return;
        }
        
        let searchTimeout = null;
        
        // Фильтрация сотрудников по совпадению
        const filterEmployees = (query) => {
            if (!query || query.length < 2) return [];
            
            const q = query.toLowerCase().trim();
            return this.allEmployees.filter(emp => {
                const fullName = (emp.full_name || '').toLowerCase();
                const dept = (emp.department || '').toLowerCase();
                const pos = (emp.position || '').toLowerCase();
                return fullName.includes(q) || dept.includes(q) || pos.includes(q);
            }).slice(0, 10);
        };
        
        // Рендер подсказок
        const renderSuggestions = (items) => {
            if (!items.length) {
                suggestionsBox.style.display = 'none';
                return;
            }
            
            let html = '';
            items.forEach(emp => {
                html += `
                    <div class="list-group-item" data-id="${emp.id}" data-name="${emp.full_name}">
                        <div class="emp-name">${emp.full_name}</div>
                        <div class="emp-dept">${emp.department || 'Отдел не указан'} ${emp.position ? '• ' + emp.position : ''}</div>
                    </div>
                `;
            });
            
            suggestionsBox.innerHTML = html;
            suggestionsBox.style.display = 'block';
            
            suggestionsBox.querySelectorAll('.list-group-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.selectEmployee(item.dataset.id, item.dataset.name);
                });
            });
        };
        
        // Обработчик ввода
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (!query) {
                hiddenInput.value = '';
                selectedInfo.style.display = 'none';
                searchInput.classList.remove('is-valid', 'is-invalid');
                suggestionsBox.style.display = 'none';
                return;
            }
            
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const matches = filterEmployees(query);
                renderSuggestions(matches);
            }, 150);
        });
        
        // Клавиатурная навигация
        searchInput.addEventListener('keydown', function(e) {
            const items = suggestionsBox.querySelectorAll('.list-group-item');
            const active = suggestionsBox.querySelector('.list-group-item.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (!items.length) return;
                if (!active) items[0].classList.add('active');
                else {
                    active.classList.remove('active');
                    (active.nextElementSibling || items[0]).classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (!items.length) return;
                if (!active) items[items.length - 1].classList.add('active');
                else {
                    active.classList.remove('active');
                    (active.previousElementSibling || items[items.length - 1]).classList.add('active');
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (active) active.click();
            } else if (e.key === 'Escape') {
                suggestionsBox.style.display = 'none';
            }
        });
        
        // Скрытие при клике вне
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#employeeSearch') && 
                !e.target.closest('#employeeSuggestions')) {
                suggestionsBox.style.display = 'none';
            }
        });
    }
    
    // ========== Выбор сотрудника ==========
    selectEmployee(id, name) {
        this.selectedEmployeeId = id;
        
        const hiddenInput = document.getElementById('employeeId');
        const searchInput = document.getElementById('employeeSearch');
        const suggestionsBox = document.getElementById('employeeSuggestions');
        const selectedInfo = document.getElementById('employeeSelected');
        
        hiddenInput.value = id;
        searchInput.value = name;
        suggestionsBox.style.display = 'none';
        selectedInfo.textContent = `✅ Выбран: ${name} (ID: ${id})`;
        selectedInfo.style.display = 'block';
        searchInput.classList.remove('is-invalid');
        searchInput.classList.add('is-valid');
    }
    
    // ========== Загрузка списка спецодежды ==========
    async loadWorkwear() {
        try {
            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.filters
            };
            
            Object.keys(params).forEach(key => {
                if (!params[key]) delete params[key];
            });
            
            const response = await API.getWorkwearItems(params);
            this.renderWorkwear(response.results || []);
            this.renderPagination(response);
        } catch (error) {
            console.error('Error loading workwear:', error);
            const tbody = document.getElementById('workwearTableBody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center py-3 text-danger">
                            <i class="fas fa-exclamation-triangle"></i> Ошибка загрузки данных
                        </td>
                    </tr>
                `;
            }
        }
    }
    
    renderWorkwear(items) {
        const container = document.getElementById('workwearTableBody');
        if (!container) return;
        
        if (items.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-3 text-muted">
                        <i class="fas fa-tshirt fa-2x d-block mb-2"></i>
                        Спецодежда не найдена
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        items.forEach(item => {
            const statusMap = {
                'active': { class: 'status-active', text: 'Активна' },
                'expiring': { class: 'status-expiring', text: 'Истекает' },
                'expiring_soon': { class: 'status-expiring', text: 'Истекает' },
                'expired': { class: 'status-expired', text: 'Просрочена' }
            };
            const status = statusMap[item.status] || statusMap.active;
            
            const days = item.days_until_expiration || 0;
            const daysColor = days <= 7 ? 'text-danger' : days <= 15 ? 'text-warning' : 'text-success';
            
            html += `
                <tr class="${item.status === 'expired' ? 'table-danger' : item.status === 'expiring' || item.status === 'expiring_soon' ? 'table-warning' : ''}">
                    <td>
                        <a href="/workwear/employees/${item.employee}/" class="text-decoration-none">
                            ${item.employee_name}
                        </a>
                    </td>
                    <td><strong>${item.name}</strong></td>
                    <td>${item.category_name}</td>
                    <td>${item.size || '-'}</td>
                    <td>${item.issue_date}</td>
                    <td>${item.expiration_date}</td>
                    <td><span class="status-badge ${status.class}">${status.text}</span></td>
                    <td class="${daysColor}">${days > 0 ? days + ' дн.' : '-'}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-success" onclick="workwearPage.returnItem(${item.id})" title="Вернуть">
                                <i class="fas fa-undo"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="workwearPage.deleteItem(${item.id})" title="Списать">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        container.innerHTML = html;
    }
    
    renderPagination(data) {
        const container = document.getElementById('paginationContainer');
        if (!container) return;
        
        if (!data || data.count <= this.pageSize) {
            container.innerHTML = '';
            return;
        }
        
        const totalPages = Math.ceil(data.count / this.pageSize);
        let html = '<nav><ul class="pagination">';
        
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage - 1}">«</a>
        </li>`;
        
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === this.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        
        html += `<li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage + 1}">»</a>
        </li>`;
        
        html += '</ul></nav>';
        container.innerHTML = html;
        
        container.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page > 0 && page <= totalPages && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadWorkwear();
                }
            });
        });
    }
    
    // ========== Сохранение спецодежды ==========
    async saveWorkwear() {
        const form = document.getElementById('addWorkwearForm');
        if (!form) return;
        
        // Проверяем, что сотрудник выбран
        const hiddenEmployeeId = document.getElementById('employeeId');
        if (!hiddenEmployeeId || !hiddenEmployeeId.value) {
            alert('⚠️ Пожалуйста, выберите сотрудника из списка подсказок');
            const searchInput = document.getElementById('employeeSearch');
            if (searchInput) {
                searchInput.classList.add('is-invalid');
                searchInput.focus();
            }
            return;
        }
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Преобразуем типы
        data.employee = parseInt(hiddenEmployeeId.value);
        data.category = parseInt(data.category);
        data.is_active = data.is_active === 'on' || data.is_active === 'true';
        
        // ✅ Проверка обязательных полей
        const requiredFields = {
            'employee': 'Сотрудник',
            'category': 'Категория',
            'name': 'Наименование',
            'issue_date': 'Дата выдачи',
            'expiration_date': 'Дата истечения'
        };
        
        const missingFields = [];
        for (const [field, label] of Object.entries(requiredFields)) {
            if (!data[field] || data[field] === '') {
                missingFields.push(label);
            }
        }
        
        if (missingFields.length > 0) {
            alert(`⚠️ Заполните обязательные поля:\n• ${missingFields.join('\n• ')}`);
            return;
        }
        
        // ✅ Проверка, что дата истечения позже даты выдачи
        const issueDate = new Date(data.issue_date);
        const expirationDate = new Date(data.expiration_date);
        
        if (expirationDate < issueDate) {
            alert('⚠️ Дата истечения не может быть раньше даты выдачи');
            return;
        }
        
        console.log('📤 Отправка данных:', data);
        
        try {
            const saveBtn = document.getElementById('saveWorkwearBtn');
            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Сохранение...';
            }
            
            await API.createWorkwearItem(data);
            
            // Закрываем модалку
            const modalEl = document.getElementById('addWorkwearModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            // Сбрасываем форму
            form.reset();
            if (hiddenEmployeeId) hiddenEmployeeId.value = '';
            const searchInput = document.getElementById('employeeSearch');
            if (searchInput) {
                searchInput.classList.remove('is-valid', 'is-invalid');
            }
            const selectedInfo = document.getElementById('employeeSelected');
            if (selectedInfo) selectedInfo.style.display = 'none';
            
            // Обновляем таблицу
            this.currentPage = 1;
            await this.loadWorkwear();
            
            this.showNotification('✅ Спецодежда успешно добавлена', 'success');
            
        } catch (error) {
            console.error('Error saving workwear:', error);
            
            let errorMsg = 'Ошибка при добавлении спецодежды';
            if (error.message) {
                errorMsg += `: ${error.message}`;
            }
            
            this.showNotification(errorMsg, 'danger');
        } finally {
            const saveBtn = document.getElementById('saveWorkwearBtn');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = 'Сохранить';
            }
        }
    }
    
    // ========== Возврат ==========
    async returnItem(id) {
        if (!confirm('Вы уверены, что хотите вернуть эту спецодежду?')) return;
        
        try {
            await API.returnWorkwearItem(id);
            await this.loadWorkwear();
            this.showNotification('Спецодежда возвращена', 'success');
        } catch (error) {
            console.error('Error returning workwear:', error);
            this.showNotification('Ошибка при возврате спецодежды', 'danger');
        }
    }
    
    // ========== Списание ==========
    async deleteItem(id) {
        if (!confirm('Вы уверены, что хотите списать эту спецодежду?')) return;
        
        try {
            await API.deleteWorkwearItem(id);
            await this.loadWorkwear();
            this.showNotification('Спецодежда списана', 'success');
        } catch (error) {
            console.error('Error deleting workwear:', error);
            this.showNotification('Ошибка при списании спецодежды', 'danger');
        }
    }
    
    // ========== Уведомления ==========
    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alert.style.zIndex = '9999';
        alert.style.maxWidth = '400px';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 5000);
    }
}

// Инициализация
let workwearPage;
document.addEventListener('DOMContentLoaded', () => {
    workwearPage = new WorkwearPage();
});