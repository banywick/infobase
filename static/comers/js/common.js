// static/comers/js/common.js
const ComersApp = (function() {
    // Приватные переменные
    const ICON_EDIT = '/static/comers/icons/icon_edit.png';
    const ICON_STATUS = '/static/comers/icons/icon_status.png';
    const ICON_DELETE = '/static/comers/icons/icon_delete.png';
    const FILTER_STORAGE_KEY = 'invoice_filters';
    
    let currentDeleteId = null;
    let currentEditId = null;
    let allData = [];
    let filteredData = [];
    
    // ===================== ПУБЛИЧНЫЕ МЕТОДЫ =====================
    const app = {
        // Геттеры для текущих ID
        getCurrentDeleteId: () => currentDeleteId,
        getCurrentEditId: () => currentEditId,
        setCurrentDeleteId: (id) => { currentDeleteId = id; },
        setCurrentEditId: (id) => { currentEditId = id; },
        
        // Данные
        getAllData: () => allData,
        getFilteredData: () => filteredData,
        setAllData: (data) => { allData = data; },
        setFilteredData: (data) => { filteredData = data; },
        
        // Иконки
        getIcons: () => ({ ICON_EDIT, ICON_STATUS, ICON_DELETE }),
        
        // ===================== ОБЩИЕ УТИЛИТЫ =====================
        getCsrfToken: function() {
            // Вариант 1: из скрытого input
            const inputToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (inputToken) return inputToken.value;
            
            // Вариант 2: из cookie
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
                
            return cookieValue || '';
        },
        
        // ===================== УВЕДОМЛЕНИЯ =====================
        showNotification: function(message, type = 'info', duration = 3000) {
            // Удаляем старые уведомления
            document.querySelectorAll('.comers-notification').forEach(el => {
                if (el.parentNode) el.parentNode.removeChild(el);
            });
            
            const notification = document.createElement('div');
            notification.className = `comers-notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    ${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}
                    <span>${message}</span>
                </div>
            `;
            
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                background: ${this.getNotificationColor(type)};
                color: white;
                border-radius: 8px;
                z-index: 10000;
                animation: slideInFromRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                font-weight: 500;
                min-width: 300px;
                max-width: 400px;
                cursor: pointer;
            `;
            
            document.body.appendChild(notification);
            
            // Автоудаление
            setTimeout(() => {
                notification.style.animation = 'slideOutToRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
                setTimeout(() => notification.remove(), 500);
            }, duration);
            
            // Клик для закрытия
            notification.addEventListener('click', () => {
                notification.style.animation = 'slideOutToRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
                setTimeout(() => notification.remove(), 500);
            });
            
            return notification;
        },
        
        getNotificationColor: function(type) {
            const colors = {
                success: 'linear-gradient(135deg, #4CAF50, #45a049)',
                error: 'linear-gradient(135deg, #f44336, #d32f2f)',
                warning: 'linear-gradient(135deg, #ff9800, #f57c00)',
                info: 'linear-gradient(135deg, #2196F3, #1976D2)'
            };
            return colors[type] || colors.info;
        },
        
        // ===================== ОБРАБОТКА ОШИБОК ФОРМ =====================
        displayFormErrors: function(formId, errors) {
            const form = document.getElementById(formId);
            if (!form) return;
            
            // Удаляем старые ошибки
            form.querySelectorAll('.error-message').forEach(el => el.remove());
            
            for (const field in errors) {
                const input = form.querySelector(`[name="${field}"]`);
                if (input) {
                    const errorElement = document.createElement('div');
                    errorElement.className = 'error-message';
                    errorElement.style.cssText = `
                        color: #dc3545;
                        font-size: 12px;
                        margin-top: 5px;
                        padding: 5px 10px;
                        background: #f8d7da;
                        border: 1px solid #f5c6cb;
                        border-radius: 4px;
                        animation: fadeIn 0.3s ease;
                    `;
                    errorElement.textContent = Array.isArray(errors[field]) 
                        ? errors[field][0] 
                        : errors[field];
                    input.after(errorElement);
                }
            }
        },
        
        clearFormErrors: function(formId) {
            const form = document.getElementById(formId);
            if (form) {
                form.querySelectorAll('.error-message').forEach(el => el.remove());
            }
        },
        
        // ===================== РАБОТА С ТАБЛИЦЕЙ =====================
        createTableRow: function(item) {
            const row = document.createElement('tr');
            row.dataset.id = item.id;
            
            // Извлекаем текстовые значения из вложенных объектов
            const commentText = item.comment ? (item.comment.text || item.comment) : '';
            const leadingName = item.leading ? (item.leading.name || item.leading) : '';
            const specialistName = item.specialist ? (item.specialist.name || item.specialist) : '';
            const statusName = item.status ? (item.status.name || item.status) : '';
            const supplierName = item.supplier ? (item.supplier.name || item.supplier) : '';
            
            row.innerHTML = `
                <td class="invoice-number">${item.invoice_number || ''}</td>
                <td class="date-cell">${item.date ? item.date.split('T')[0] : ''}</td>
                <td class="supplier-cell">${supplierName}</td>
                <td class="article-cell">${item.article || ''}</td>
                <td>${item.name || ''}</td>
                <td>${item.unit || ''}</td>
                <td class="quantity-cell">${item.quantity || ''}</td>
                <td class="comment-cell">${commentText}</td>
                <td>${item.description_problem || ''}</td>
                <td>${specialistName}</td>
                <td>${leadingName}</td>
                <td class="status-cell">${statusName}</td>
                <td class="description-cell">${item.description || ''}</td>
                <td>
                    <div class="action_cell_table">
                        <div class="edit_invoice_button edit_button" data-id="${item.id}">
                            <img src="${ICON_EDIT}" alt="Редактировать">
                            <div class="open-btn" data-popup="popup5">Редактировать</div>
                        </div>
                        <div class="edit_invoice_button edit_status_button" data-id="${item.id}">
                            <img src="${ICON_STATUS}" alt="Статус">
                            <div class="open-btn" data-popup="popup6">Статус</div>
                        </div>
                        <div class="edit_invoice_button delete_button" data-id="${item.id}">
                            <img src="${ICON_DELETE}" alt="Удалить">
                            <div class="open-btn" data-popup="popup7">Удалить</div>
                        </div>
                    </div>
                </td>
            `;
            
            return row;
        },
        
        addRowToTable: function(item, position = 'bottom') {
            const tableBody = document.getElementById('invoiceTableBody');
            if (!tableBody) {
                console.error('Элемент invoiceTableBody не найден');
                return null;
            }
            
            const newRow = this.createTableRow(item);
            newRow.classList.add('new-row');
            
            if (position === 'top' && tableBody.firstChild) {
                tableBody.insertBefore(newRow, tableBody.firstChild);
            } else {
                // Добавляем В КОНЕЦ (снизу таблицы)
                tableBody.appendChild(newRow);
            }
            
            // Удаляем класс анимации после завершения
            setTimeout(() => {
                newRow.classList.remove('new-row');
                newRow.style.backgroundColor = '';
            }, 1500);
            
            return newRow;
        },
        
        updateRowInTable: function(item) {
            const row = document.querySelector(`tr[data-id="${item.id}"]`);
            if (!row) return this.addRowToTable(item);
            
            const newRow = this.createTableRow(item);
            row.parentNode.replaceChild(newRow, row);
            return newRow;
        },
        
        removeRowFromTable: function(itemId) {
            const row = document.querySelector(`tr[data-id="${itemId}"]`);
            if (row) {
                row.classList.add('removing-row');
                setTimeout(() => {
                    if (row.parentNode) row.parentNode.removeChild(row);
                }, 300);
                return true;
            }
            return false;
        },
        
        renderTable: function(data = null) {
            const tableBody = document.getElementById('invoiceTableBody');
            if (!tableBody) {
                console.error('Элемент invoiceTableBody не найден');
                return;
            }
            
            const renderData = data || filteredData || allData || [];
            
            tableBody.innerHTML = '';
            
            if (renderData.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="14" style="text-align: center; padding: 20px;">
                            Нет данных
                        </td>
                    </tr>
                `;
                return;
            }
            
            renderData.forEach(item => {
                const row = this.createTableRow(item);
                tableBody.appendChild(row);
            });
            
            console.log(`Отображено ${renderData.length} строк`);
        },
        
        // ===================== ФИЛЬТРЫ =====================
        saveFilters: function(filters) {
            localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
        },
        
        loadFilters: function() {
            const saved = localStorage.getItem(FILTER_STORAGE_KEY);
            return saved ? JSON.parse(saved) : null;
        },
        
        clearFilters: function() {
            localStorage.removeItem(FILTER_STORAGE_KEY);
        },
        
        // ===================== ПОПАПЫ =====================
        closeActivePopup: function() {
            const activePopup = document.querySelector('.my-popup.active');
            if (activePopup) {
                activePopup.classList.remove('active');
                return true;
            }
            return false;
        },
        
        // ===================== API ЗАПРОСЫ =====================
        fetchData: async function(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json',
                }
            };
            
            const mergedOptions = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, mergedOptions);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Fetch error:', error);
                throw error;
            }
        },
        
        // ===================== ЗАГРУЗКА ВСЕХ ДАННЫХ =====================
        loadAllData: async function() {
            try {
                const data = await this.fetchData('/comers/get_all_positions/');
                allData = data;
                filteredData = [...data];
                this.renderTable();
                return data;
            } catch (error) {
                console.error('Error loading data:', error);
                this.showNotification('Ошибка загрузки данных', 'error');
                throw error;
            }
        },
        
        // ===================== ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ РЕДАКТИРОВАНИЯ =====================
        loadInvoiceForEdit: async function(invoiceId) {
            try {
                // Используем эндпоинт для редактирования
                const data = await this.fetchData(`/comers/edit_invoices/${invoiceId}/`);
                return data;
            } catch (error) {
                console.error('Error loading invoice for edit:', error);
                this.showNotification('Ошибка загрузки данных для редактирования', 'error');
                throw error;
            }
        },
        
        // ===================== ИНИЦИАЛИЗАЦИЯ =====================
        init: function() {
            this.loadAnimationStyles();
            this.setupTableEventDelegation();
            return this;
        },
        
        // Делегирование событий для таблицы
        setupTableEventDelegation: function() {
            const tableBody = document.getElementById('invoiceTableBody');
            if (!tableBody) return;
            
            tableBody.addEventListener('click', (e) => {
                // Находим ближайшую кнопку действия
                const actionButton = e.target.closest('.edit_invoice_button');
                if (!actionButton) return;
                
                const invoiceId = actionButton.dataset.id;
                if (!invoiceId) return;
                
                console.log('Клик по кнопке:', actionButton.classList, 'ID:', invoiceId);
                
                // Устанавливаем ID в зависимости от типа кнопки
                if (actionButton.classList.contains('delete_button')) {
                    this.setCurrentDeleteId(invoiceId);
                    console.log('Установлен ID для удаления:', invoiceId);
                } else if (actionButton.classList.contains('edit_button')) {
                    this.setCurrentEditId(invoiceId);
                    console.log('Установлен ID для редактирования:', invoiceId);
                } else if (actionButton.classList.contains('edit_status_button')) {
                    this.setCurrentEditId(invoiceId);
                    console.log('Установлен ID для статуса:', invoiceId);
                }
            });
        },
        
        loadAnimationStyles: function() {
            if (!document.querySelector('#animation-styles')) {
                const style = document.createElement('style');
                style.id = 'animation-styles';
                style.textContent = `
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(-10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    
                    @keyframes slideInFromRight {
                        0% { transform: translateX(100%) scale(0.8); opacity: 0; }
                        70% { transform: translateX(-10px) scale(1.05); }
                        100% { transform: translateX(0) scale(1); opacity: 1; }
                    }
                    
                    @keyframes slideOutToRight {
                        0% { transform: translateX(0) scale(1); opacity: 1; }
                        30% { transform: translateX(-10px) scale(1.05); }
                        100% { transform: translateX(100%) scale(0.8); opacity: 0; }
                    }
                    
                    @keyframes slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                    
                    @keyframes slideOut {
                        from { transform: translateX(0); opacity: 1; }
                        to { transform: translateX(100%); opacity: 0; }
                    }
                    
                    /* Анимация для новых строк */
                    @keyframes slideInFromBottom {
                        from { 
                            opacity: 0; 
                            transform: translateY(20px); 
                            max-height: 0;
                        }
                        to { 
                            opacity: 1; 
                            transform: translateY(0); 
                            max-height: 100px;
                        }
                    }
                    
                    .new-row {
                        animation: slideInFromBottom 0.5s ease forwards;
                        background-color: #e8f5e9 !important;
                        transition: background-color 1.5s ease;
                    }
                    
                    .removing-row {
                        animation: slideOut 0.3s ease forwards;
                        opacity: 0;
                        transform: translateX(-100%);
                    }
                    
                    /* Подсветка выбранных фильтров */
                    .filter-selected {
                        background-color: #e8f5e9 !important;
                        border-color: #4caf50 !important;
                        color: #2e7d32 !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    };
    
    return app.init();
})();

// Экспортируем в глобальную область видимости
if (typeof window !== 'undefined') {
    window.ComersApp = ComersApp;
}