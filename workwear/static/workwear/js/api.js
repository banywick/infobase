// API клиент для работы с бэкендом
const API = {
    baseURL: '/workwear/api/',
    
    // Получение CSRF токена
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    },
    
    // Общие заголовки
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
        };
    },
    
    // GET запрос
    async get(endpoint, params = {}) {
        const url = new URL(this.baseURL + endpoint, window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
                url.searchParams.append(key, params[key]);
            }
        });
        
        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(),
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    
    // POST запрос
    async post(endpoint, data) {
        const response = await fetch(this.baseURL + endpoint, {
            method: 'POST',
            headers: this.getHeaders(),
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    
    // PUT запрос
    async put(endpoint, data) {
        const response = await fetch(this.baseURL + endpoint, {
            method: 'PUT',
            headers: this.getHeaders(),
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    
    // PATCH запрос
    async patch(endpoint, data) {
        const response = await fetch(this.baseURL + endpoint, {
            method: 'PATCH',
            headers: this.getHeaders(),
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    
    // DELETE запрос
    async delete(endpoint) {
        const response = await fetch(this.baseURL + endpoint, {
            method: 'DELETE',
            headers: this.getHeaders(),
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    
    // ============================================================
    // ========== СОТРУДНИКИ (Employees) ==========================
    // ============================================================
    
    /**
     * Получить список сотрудников с пагинацией и фильтрацией
     * @param {Object} params - Параметры фильтрации
     * @param {string} params.search - Поиск по имени, фамилии, табельному номеру, отделу
     * @param {string} params.department - Фильтр по отделу
     * @param {string} params.status - Фильтр по статусу спецодежды: 'expired', 'expiring', 'ok'
     * @param {number} params.page - Номер страницы
     * @param {number} params.page_size - Количество элементов на странице
     * @returns {Promise<Object>} Объект с пагинацией и результатами
     */
    async getEmployees(params = {}) {
        return this.get('employees/', params);
    },
    
    /**
     * Получить сотрудника по ID
     * @param {number} id - ID сотрудника
     * @returns {Promise<Object>} Данные сотрудника
     */
    async getEmployee(id) {
        return this.get(`employees/${id}/`);
    },
    
    /**
     * Создать нового сотрудника
     * @param {Object} data - Данные сотрудника
     * @param {number} data.user_id - ID пользователя
     * @param {string} data.employee_id - Табельный номер
     * @param {string} data.department - Отдел
     * @param {string} data.position - Должность
     * @param {string} data.email - Email
     * @param {string} data.phone - Телефон (опционально)
     * @param {string} data.photo - URL фото (опционально)
     * @returns {Promise<Object>} Созданный сотрудник
     */
    async createEmployee(data) {
        return this.post('employees/', data);
    },
    
    /**
     * Обновить данные сотрудника
     * @param {number} id - ID сотрудника
     * @param {Object} data - Данные для обновления
     * @returns {Promise<Object>} Обновленный сотрудник
     */
    async updateEmployee(id, data) {
        return this.put(`employees/${id}/`, data);
    },
    
    /**
     * Частично обновить данные сотрудника
     * @param {number} id - ID сотрудника
     * @param {Object} data - Данные для обновления
     * @returns {Promise<Object>} Обновленный сотрудник
     */
    async patchEmployee(id, data) {
        return this.patch(`employees/${id}/`, data);
    },
    
    /**
     * Деактивировать сотрудника (soft delete)
     * @param {number} id - ID сотрудника
     * @returns {Promise<Object>} Результат операции
     */
    async deleteEmployee(id) {
        return this.delete(`employees/${id}/`);
    },
    
    /**
     * Получить всю спецодежду сотрудника
     * @param {number} id - ID сотрудника
     * @param {Object} params - Параметры фильтрации
     * @param {string} params.status - Фильтр по статусу: 'expired', 'expiring_soon'
     * @returns {Promise<Array>} Список спецодежды
     */
    async getEmployeeWorkwear(id, params = {}) {
        return this.get(`employees/${id}/workwear/`, params);
    },
    
    /**
     * Получить историю изменений спецодежды сотрудника
     * @param {number} id - ID сотрудника
     * @returns {Promise<Array>} История изменений
     */
    async getEmployeeHistory(id) {
        return this.get(`employees/${id}/history/`);
    },
    
    /**
     * Получить полную информацию о сотруднике (профиль + спецодежда + история)
     * @param {number} id - ID сотрудника
     * @returns {Promise<Object>} Полные данные сотрудника
     */
    async getEmployeeFullData(id) {
        const [employee, workwear, history] = await Promise.all([
            this.getEmployee(id),
            this.getEmployeeWorkwear(id),
            this.getEmployeeHistory(id)
        ]);
        return { employee, workwear, history };
    },
    
    /**
     * Получить всех сотрудников (без пагинации, для селектов)
     * @param {Object} params - Дополнительные параметры
     * @returns {Promise<Array>} Список всех сотрудников
     */
    async getAllEmployees(params = {}) {
        const response = await this.get('employees/', { ...params, page_size: 1000 });
        return response.results || [];
    },
    
    // ============================================================
    // ========== СПЕЦОДЕЖДА (Workwear Items) =====================
    // ============================================================
    
    /**
     * Получить список спецодежды с пагинацией и фильтрацией
     * @param {Object} params - Параметры фильтрации
     * @param {number} params.employee_id - ID сотрудника
     * @param {number} params.category - ID категории
     * @param {string} params.status - Статус: 'active', 'expired', 'expiring'
     * @param {string} params.search - Поиск по названию, серийному номеру, сотруднику
     * @param {string} params.expiration_from - Дата истечения с (YYYY-MM-DD)
     * @param {string} params.expiration_to - Дата истечения по (YYYY-MM-DD)
     * @param {number} params.page - Номер страницы
     * @param {number} params.page_size - Количество элементов на странице
     * @returns {Promise<Object>} Объект с пагинацией и результатами
     */
    async getWorkwearItems(params = {}) {
        return this.get('workwear-items/', params);
    },
    
    /**
     * Получить предмет спецодежды по ID
     * @param {number} id - ID предмета
     * @returns {Promise<Object>} Данные предмета
     */
    async getWorkwearItem(id) {
        return this.get(`workwear-items/${id}/`);
    },
    
    /**
     * Создать новый предмет спецодежды
     * @param {Object} data - Данные предмета
     * @param {number} data.employee - ID сотрудника
     * @param {number} data.category - ID категории
     * @param {string} data.name - Наименование
     * @param {string} data.serial_number - Серийный номер (опционально)
     * @param {string} data.size - Размер (опционально)
     * @param {string} data.color - Цвет (опционально)
     * @param {string} data.issue_date - Дата выдачи (YYYY-MM-DD)
     * @param {string} data.expiration_date - Дата истечения (YYYY-MM-DD, опционально)
     * @param {string} data.notes - Примечания (опционально)
     * @returns {Promise<Object>} Созданный предмет
     */
    async createWorkwearItem(data) {
        return this.post('workwear-items/', data);
    },
    
    /**
     * Обновить предмет спецодежды
     * @param {number} id - ID предмета
     * @param {Object} data - Данные для обновления
     * @returns {Promise<Object>} Обновленный предмет
     */
    async updateWorkwearItem(id, data) {
        return this.put(`workwear-items/${id}/`, data);
    },
    
    /**
     * Частично обновить предмет спецодежды
     * @param {number} id - ID предмета
     * @param {Object} data - Данные для обновления
     * @returns {Promise<Object>} Обновленный предмет
     */
    async patchWorkwearItem(id, data) {
        return this.patch(`workwear-items/${id}/`, data);
    },
    
    /**
     * Списать предмет спецодежды (soft delete)
     * @param {number} id - ID предмета
     * @returns {Promise<Object>} Результат операции
     */
    async deleteWorkwearItem(id) {
        return this.delete(`workwear-items/${id}/`);
    },
    
    /**
     * Вернуть спецодежду
     * @param {number} id - ID предмета
     * @param {Object} data - Дополнительные данные
     * @param {string} data.description - Описание возврата
     * @returns {Promise<Object>} Результат операции
     */
    async returnWorkwearItem(id, data = {}) {
        return this.post(`workwear-items/${id}/return/`, data);
    },
    
    // ============================================================
    // ========== ИСТЕКАЮЩИЕ / ПРОСРОЧЕННЫЕ =======================
    // ============================================================
    
    /**
     * Получить все предметы с истекающим сроком (в ближайшие 30 дней)
     * @param {Object} params - Параметры фильтрации
     * @param {string} params.department - Фильтр по отделу
     * @returns {Promise<Array>} Список предметов
     */
    async getExpiringItems(params = {}) {
        return this.get('expiring-items/', params);
    },
    
    /**
     * Получить все просроченные предметы
     * @param {Object} params - Параметры фильтрации
     * @param {string} params.department - Фильтр по отделу
     * @returns {Promise<Array>} Список предметов
     */
    async getExpiredItems(params = {}) {
        return this.get('expired-items/', params);
    },
    
    /**
     * Получить предметы с истекающим сроком для конкретного сотрудника
     * @param {number} employeeId - ID сотрудника
     * @returns {Promise<Array>} Список предметов
     */
    async getEmployeeExpiringItems(employeeId) {
        const items = await this.getEmployeeWorkwear(employeeId, { status: 'expiring_soon' });
        return items;
    },
    
    /**
     * Получить просроченные предметы для конкретного сотрудника
     * @param {number} employeeId - ID сотрудника
     * @returns {Promise<Array>} Список предметов
     */
    async getEmployeeExpiredItems(employeeId) {
        const items = await this.getEmployeeWorkwear(employeeId, { status: 'expired' });
        return items;
    },
    
    // ============================================================
    // ========== КАТЕГОРИИ (Categories) ===========================
    // ============================================================
    
    /**
     * Получить все категории
     * @returns {Promise<Array>} Список категорий
     */
    async getCategories() {
        return this.get('categories/');
    },
    
    /**
     * Получить категорию по ID
     * @param {number} id - ID категории
     * @returns {Promise<Object>} Данные категории
     */
    async getCategory(id) {
        return this.get(`categories/${id}/`);
    },
    
    /**
     * Создать новую категорию
     * @param {Object} data - Данные категории
     * @param {string} data.name - Название категории
     * @param {string} data.description - Описание
     * @param {number} data.standard_lifespan - Стандартный срок эксплуатации (дней)
     * @returns {Promise<Object>} Созданная категория
     */
    async createCategory(data) {
        return this.post('categories/', data);
    },
    
    /**
     * Обновить категорию
     * @param {number} id - ID категории
     * @param {Object} data - Данные для обновления
     * @returns {Promise<Object>} Обновленная категория
     */
    async updateCategory(id, data) {
        return this.put(`categories/${id}/`, data);
    },
    
    /**
     * Деактивировать категорию
     * @param {number} id - ID категории
     * @returns {Promise<Object>} Результат операции
     */
    async deleteCategory(id) {
        return this.delete(`categories/${id}/`);
    },
    
    /**
     * Получить категории в виде объекта {id: name} для селектов
     * @returns {Promise<Object>} Объект с категориями
     */
    async getCategoriesMap() {
        const categories = await this.getCategories();
        const map = {};
        categories.forEach(cat => {
            if (cat.is_active) {
                map[cat.id] = cat.name;
            }
        });
        return map;
    },
    
    // ============================================================
    // ========== ДАШБОРД (Dashboard) =============================
    // ============================================================
    
    /**
     * Получить статистику для дашборда
     * @returns {Promise<Object>} Статистика
     */
    async getDashboardStats() {
        return this.get('dashboard/stats/');
    },
    
    /**
     * Получить статистику по сотрудникам
     * @returns {Promise<Object>} Статистика по сотрудникам
     */
    async getEmployeeStats() {
        const stats = await this.getDashboardStats();
        return {
            total: stats.total_employees || 0,
            expiring: stats.expiring_employees || 0,
            expired: stats.expired_employees || 0
        };
    },
    
    /**
     * Получить статистику по спецодежде
     * @returns {Promise<Object>} Статистика по спецодежде
     */
    async getWorkwearStats() {
        const stats = await this.getDashboardStats();
        return {
            total: stats.total_workwear || 0,
            active: stats.total_workwear - stats.expiring_items - stats.expired_items || 0,
            expiring: stats.expiring_items || 0,
            expired: stats.expired_items || 0
        };
    },
    
    // ============================================================
    // ========== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ===========================
    // ============================================================
    
    /**
     * Поиск сотрудников по имени или фамилии
     * @param {string} query - Поисковый запрос
     * @param {number} limit - Лимит результатов
     * @returns {Promise<Array>} Список сотрудников
     */
    async searchEmployees(query, limit = 10) {
        if (!query || query.length < 2) return [];
        const response = await this.get('employees/', { 
            search: query, 
            page_size: limit 
        });
        return response.results || [];
    },
    
    /**
     * Поиск спецодежды по названию или серийному номеру
     * @param {string} query - Поисковый запрос
     * @param {number} limit - Лимит результатов
     * @returns {Promise<Array>} Список предметов
     */
    async searchWorkwear(query, limit = 10) {
        if (!query || query.length < 2) return [];
        const response = await this.get('workwear-items/', { 
            search: query, 
            page_size: limit 
        });
        return response.results || [];
    },
    
    /**
     * Получить количество предметов по категориям
     * @returns {Promise<Object>} Количество предметов по категориям
     */
    async getCategoryStats() {
        const categories = await this.getCategories();
        const stats = {};
        
        for (const cat of categories) {
            if (!cat.is_active) continue;
            const items = await this.getWorkwearItems({ category: cat.id, page_size: 1 });
            stats[cat.name] = items.count || 0;
        }
        
        return stats;
    },
    
    /**
     * Экспорт данных в CSV (если реализовано на бэкенде)
     * @param {string} endpoint - Эндпоинт для экспорта
     * @param {Object} params - Параметры фильтрации
     * @returns {Promise<string>} CSV данные
     */
    async exportCSV(endpoint, params = {}) {
        const url = new URL(this.baseURL + endpoint, window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
                url.searchParams.append(key, params[key]);
            }
        });
        url.searchParams.append('format', 'csv');
        
        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(),
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    },
    
    /**
     * Загрузка файла (для будущего расширения)
     * @param {string} endpoint - Эндпоинт для загрузки
     * @param {FormData} formData - Данные формы
     * @returns {Promise<Object>} Результат загрузки
     */
    async uploadFile(endpoint, formData) {
        const response = await fetch(this.baseURL + endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            },
            credentials: 'include',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
};

// Экспортируем API для использования в других файлах
window.API = API;

// Для использования в модулях (если нужно)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}