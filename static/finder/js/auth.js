document.getElementById('loginButton').addEventListener('click', function(e) {
    e.preventDefault();
    
    // Получаем значения полей
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Сбрасываем предыдущие ошибки
    document.getElementById('usernameError').textContent = '';
    document.getElementById('passwordError').textContent = '';
    
    // Валидация полей
    let isValid = true;
    
    if (!username.trim()) {
        document.getElementById('usernameError').textContent = 'Введите логин';
        isValid = false;
    }
    
    if (!password.trim()) {
        document.getElementById('passwordError').textContent = 'Введите пароль';
        isValid = false;
    }
    
    if (!isValid) return;
    
    // Показываем индикатор загрузки
    const button = document.getElementById('loginButton');
    const originalText = button.textContent;
    button.textContent = 'Загрузка...';
    button.disabled = true;
    
    // Отправляем запрос на сервер
    fetch('/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        // Восстанавливаем кнопку
        button.textContent = originalText;
        button.disabled = false;
        
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка аутентификации');
            });
        }
        return response.json();
    })
    .then(data => {
        // Успешная аутентификация
        console.log('Успешный вход:', data);
        
        // Можно перенаправить пользователя или обновить интерфейс
        window.location.href = '/'; // Перенаправление на главную страницу
    })
    .catch(error => {
        // Обработка ошибок
        console.error('Ошибка:', error);
        
        // Показываем общую ошибку аутентификации
        document.getElementById('passwordError').textContent = error.message;
        
        // Можно также сбросить поле пароля для безопасности
        document.getElementById('password').value = '';
    });
});

// Обработка нажатия Enter в полях формы
document.getElementById('loginForm').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('loginButton').click();
    }
});




// Функция для получения CSRF токена
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Функция для показа уведомления
function showNotification(message, type = 'success') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 1000;
        font-family: Arial, sans-serif;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Добавляем анимацию
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Добавляем уведомление на страницу
    document.body.appendChild(notification);
    
    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 300);
    }, 3000);
    
    return notification;
}

function logoutUser() {
    // Показываем индикатор загрузки на кнопке
    const logoutButton = document.getElementById('logoutButton');
    const originalText = logoutButton.textContent;
    logoutButton.textContent = 'Выход...';
    logoutButton.disabled = true;
    
    fetch('/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        credentials: 'same-origin' // Важно для отправки сессионных куки
    })
    .then(response => {
        if (response.ok) {
            // Показываем уведомление об успешном выходе
            showNotification('Вы вышли из учетной записи');
            
            // Ждем пока уведомление покажется и через секунду перенаправляем
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            throw new Error('Ошибка при выходе из системы');
        }
    })
    .catch(error => {
        console.error('Ошибка выхода:', error);
        
        // Восстанавливаем кнопку
        logoutButton.textContent = originalText;
        logoutButton.disabled = false;
        
        // Показываем уведомление об ошибке
        showNotification('Не удалось выйти. Попробуйте еще раз.', 'error');
    });
}

// Добавляем слушатель кнопки по клику
document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.getElementById('logoutButton');
    
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutUser);
    }
});