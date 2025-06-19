document.addEventListener('DOMContentLoaded', function() {
    // Элементы формы
    const noteForm = document.getElementById('noteForm');
    const noteTextarea = document.querySelector('.note_textarea');
    
    // Инициализация уведомлений
    initNotifications();

    // Обработчик отправки формы
    noteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const noteText = noteTextarea.value.trim();
        
        // Валидация
        if (!noteText) {
            showNotification('Пожалуйста, введите текст заметки', false);
            noteTextarea.focus();
            return;
        }

        // Получаем ID пользователя
        const userId = getCurrentUserId();
        if (!userId) {
            showNotification('Ошибка: не удалось определить пользователя', false);
            return;
        }

        // Отправка данных
        saveNote(noteText, userId)
            .then(data => {
                showNotification('Заметка успешно сохранена!');
                resetForm();
                
                // Закрытие popup если есть функция
                if (typeof window.closeNotePopup === 'function') {
                    window.closeNotePopup();
                }
                
                // Обновление списка если есть функция
                if (typeof window.refreshNotesList === 'function') {
                    window.refreshNotesList();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'Произошла ошибка', false);
            });
    });

    // Функция сохранения заметки
    async function saveNote(text, userId) {
        const csrfToken = getCSRFToken();
        const data = {
            text: text,
            user: parseInt(userId)
        };

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

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка сервера');
        }

        return await response.json();
    }

    // Функция получения ID пользователя
    function getCurrentUserId() {
        // Вариант 1: из data-атрибута формы
        if (noteForm.dataset.userId) {
            return noteForm.dataset.userId;
        }
        
        // Вариант 2: из глобальной переменной
        if (window.currentUserId) {
            return window.currentUserId;
        }
        
        // Вариант 3: из скрытого поля в форме
        const userIdInput = noteForm.querySelector('[name="user_id"]');
        if (userIdInput) {
            return userIdInput.value;
        }
        
        return null;
    }

    // Функция получения CSRF токена
    function getCSRFToken() {
        // Из cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        // Или из формы
        return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Инициализация системы уведомлений
    function initNotifications() {
        // Создаем контейнер если его нет
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
    }

    // Функция показа уведомления
    function showNotification(message, isSuccess = true) {
        const container = document.getElementById('notification-container') || document.body;
        const notification = document.createElement('div');
        notification.className = `notification ${isSuccess ? 'success' : 'error'}`;
        
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <span class="notification-close">&times;</span>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Закрытие по клику
        notification.querySelector('.notification-close').addEventListener('click', () => {
            closeNotification(notification);
        });
        
        // Автоматическое закрытие
        setTimeout(() => {
            closeNotification(notification);
        }, 3000);
    }

    // Функция закрытия уведомления
    function closeNotification(notification) {
        notification.classList.remove('show');
        notification.classList.add('hide');
        
        // Удаление после анимации
        setTimeout(() => {
            notification.remove();
        }, 300);
    }

    // Сброс формы
    function resetForm() {
        noteTextarea.value = '';
        noteTextarea.focus();
    }
});