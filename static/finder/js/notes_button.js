// notes_button.js - упрощенная версия без проверки пользователя

console.log('notes_button.js загружен');

class NotesButton {
    constructor() {
        console.log('NotesButton конструктор вызван');
        this.button = this.findButton();
        this.init();
    }

    findButton() {
        const button = document.querySelector('.note_button button');
        console.log('Найдена кнопка:', button);
        return button;
    }

    init() {
        if (!this.button) {
            console.error('Кнопка не найдена');
            return;
        }
        
        // Добавляем обработчик
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleClick(e);
        });
        
        console.log('Кнопка инициализирована');
    }

    async handleClick(e) {
        console.log('Начало обработки клика');
        
        // Показываем сообщение о начале
        this.showNotification('Собираем данные...', 'info');
        
        // Собираем данные
        const noteText = this.getNoteText();
        console.log('Текст заметки:', noteText);
        
        if (!noteText.trim()) {
            this.showNotification('Нет данных для сохранения', 'error');
            return;
        }
        
        // Показываем индикатор загрузки
        this.showLoading(true);
        
        try {
            // Сохраняем заметку
            const result = await this.saveNote(noteText);
            console.log('Результат сохранения:', result);
            
            // Показываем уведомление об успехе
            this.showNotification('✅ Заметка успешно сохранена!', 'success');
            
            // Блокируем кнопку после успешного сохранения
            this.disableButton();
            
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showNotification(
                error.message || 'Ошибка при сохранении заметки',
                'error'
            );
        } finally {
            // Скрываем индикатор загрузки
            this.showLoading(false);
        }
    }

    getNoteText() {
        // Собираем все данные
        const data = {
            name: this.getElementText('position_name'),
            article: this.getElementText('position_article'),
            project: this.getElementText('project_name'),
            quantity: this.getElementText('total_quantity'),
            unit: this.getElementText('unit'),
            allProjects: this.getElementText('count_projects')
        };
        
        // Форматируем текст заметки
        let noteText = '=== ИНФОРМАЦИЯ О ПОЗИЦИИ ===\n\n';
        
        if (data.name) noteText += `Наименование: ${data.name}\n`;
        if (data.article) noteText += `Артикул: ${data.article}\n`;
        if (data.project) noteText += `Проект: ${data.project}\n`;
        if (data.quantity) noteText += `Количество: ${data.quantity} ${data.unit || ''}\n`;
        
        
        return noteText;
    }

    getElementText(elementId) {
        const element = document.getElementById(elementId);
        return element ? element.textContent.trim() : '';
    }

    async saveNote(noteText) {
        console.log('Отправка заметки на сервер...');
        
        const csrfToken = this.getCSRFToken();
        
        if (!csrfToken) {
            throw new Error('CSRF токен не найден');
        }
        
        // Подготовка данных для отправки
        const data = {
            text: noteText
            // user будет автоматически добавлен на сервере из request.user
        };
        
        console.log('Отправляемые данные:', data);
        
        const response = await fetch('/notes/add_note/', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        });
        
        console.log('Ответ сервера:', response.status, response.statusText);
        
        if (!response.ok) {
            let errorMessage = 'Ошибка сервера';
            try {
                const errorData = await response.json();
                console.log('Данные ошибки:', errorData);
                errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
            } catch (e) {
                errorMessage = `HTTP ошибка: ${response.status}`;
            }
            throw new Error(errorMessage);
        }
        
        return await response.json();
    }

    getCSRFToken() {
        // 1. Из скрытого поля Django
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            console.log('CSRF найден в input');
            return csrfInput.value;
        }
        
        // 2. Из cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieValue) {
            console.log('CSRF найден в cookie');
            return cookieValue;
        }
        
        console.warn('CSRF токен не найден');
        return '';
    }

    showLoading(show) {
        if (show) {
            this.button.disabled = true;
            this.button.style.opacity = '0.7';
            this.button.style.cursor = 'wait';
            this.button.innerHTML = 'Сохранение...';
        } else {
            this.button.disabled = false;
            this.button.style.opacity = '1';
            this.button.style.cursor = 'pointer';
            this.button.textContent = 'Добавить в заметки';
        }
    }

    disableButton() {
        this.button.disabled = true;
        this.button.style.opacity = '0.6';
        this.button.style.cursor = 'default';
        this.button.innerHTML = '✅ Добавлено';
    }

    showNotification(message, type = 'info') {
        console.log('Показ уведомления:', message, type);
        
        // Определяем цвет в зависимости от типа
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            info: '#2196F3',
            warning: '#ff9800'
        };
        
        const color = colors[type] || colors.info;
        
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-left: 4px solid ${color};
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            max-width: 400px;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #333; font-size: 14px; font-weight: 500;">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: #999; font-size: 20px; cursor: pointer; margin-left: 10px; padding: 0 5px;">
                    &times;
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Автоматическое закрытие
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }
}

// Инициализация
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM загружен, ищем кнопку заметок');
        setTimeout(() => {
            const button = document.querySelector('.note_button button');
            if (button) {
                window.notesButton = new NotesButton();
                console.log('NotesButton создан');
            }
        }, 100);
    });
} else {
    console.log('DOM уже загружен, ищем кнопку');
    setTimeout(() => {
        const button = document.querySelector('.note_button button');
        if (button) {
            window.notesButton = new NotesButton();
            console.log('NotesButton создан');
        }
    }, 100);
}

// Тестовая функция
window.testNotesButton = function() {
    if (window.notesButton) {
        window.notesButton.handleClick(new Event('click'));
    } else {
        alert('Кнопка не инициализирована');
    }
};