// Функции для управления отображением ошибок
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    const inputElement = document.getElementById(elementId.replace('Error', ''));
    
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('visible');
        errorElement.style.display = 'block';
    }
    
    if (inputElement) {
        inputElement.classList.add('error-input');
    }
}

function hideError(elementId) {
    const errorElement = document.getElementById(elementId);
    const inputElement = document.getElementById(elementId.replace('Error', ''));
    
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('visible');
        errorElement.style.display = 'none';
    }
    
    if (inputElement) {
        inputElement.classList.remove('error-input');
    }
}

function hideAllErrors() {
    hideError('usernameError');
    hideError('passwordError');
}

// НОВАЯ ФУНКЦИЯ: Полная очистка всех ошибок
function resetAllErrors() {
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Очищаем сообщения об ошибках
    if (usernameError) {
        usernameError.textContent = '';
        usernameError.classList.remove('visible');
        usernameError.style.display = 'none';
    }
    
    if (passwordError) {
        passwordError.textContent = '';
        passwordError.classList.remove('visible');
        passwordError.style.display = 'none';
    }
    
    // Убираем красную подсветку с полей
    if (usernameInput) {
        usernameInput.classList.remove('error-input');
        usernameInput.style.borderColor = '';
        usernameInput.style.boxShadow = '';
        usernameInput.value = ''; // Очищаем поле (опционально)
    }
    
    if (passwordInput) {
        passwordInput.classList.remove('error-input');
        passwordInput.style.borderColor = '';
        passwordInput.style.boxShadow = '';
        passwordInput.value = ''; // Очищаем поле (опционально)
    }
}

// Обработчик входа
document.getElementById('loginButton').addEventListener('click', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    hideAllErrors();
    
    let isValid = true;
    
    if (!username.trim()) {
        showError('usernameError', 'Введите логин');
        isValid = false;
    }
    
    if (!password.trim()) {
        showError('passwordError', 'Введите пароль');
        isValid = false;
    }
    
    if (!isValid) return;
    
    const button = document.getElementById('loginButton');
    const originalText = button.textContent;
    button.textContent = 'Загрузка...';
    button.disabled = true;
    
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
        showNotification('Успешный вход!', 'success');
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showError('passwordError', error.message);
        document.getElementById('password').value = '';
        showNotification(error.message, 'error');
    });
});

// Очистка ошибок при вводе текста
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

if (usernameInput) {
    usernameInput.addEventListener('input', function() {
        hideError('usernameError');
    });
}

if (passwordInput) {
    passwordInput.addEventListener('input', function() {
        hideError('passwordError');
    });
}

// Обработка нажатия Enter
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('loginButton').click();
        }
    });
}

// ВАЖНО: Очищаем ошибки при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    resetAllErrors();
    
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutUser);
    }
});

// Если popup открывается по кнопке, добавьте очистку
// Например, если у вас есть кнопка открытия popup:
const openPopupButton = document.getElementById('openPopupButton');
if (openPopupButton) {
    openPopupButton.addEventListener('click', function() {
        // Очищаем ошибки перед открытием popup
        setTimeout(() => {
            resetAllErrors();
        }, 100);
    });
}

// Если используете Bootstrap модальное окно
$(document).ready(function() {
    $('#yourModalId').on('show.bs.modal', function() {
        resetAllErrors();
    });
});

// Функция для получения CSRF токена
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Функция для показа уведомления
function showNotification(message, type = 'success') {
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
    
    document.body.appendChild(notification);
    
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

// Функция выхода из системы
function logoutUser() {
    const logoutButton = document.getElementById('logoutButton');
    if (!logoutButton) return;
    
    const originalText = logoutButton.textContent;
    logoutButton.textContent = 'Выход...';
    logoutButton.disabled = true;
    
    fetch('/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            showNotification('Вы вышли из учетной записи');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            throw new Error('Ошибка при выходе из системы');
        }
    })
    .catch(error => {
        console.error('Ошибка выхода:', error);
        logoutButton.textContent = originalText;
        logoutButton.disabled = false;
        showNotification('Не удалось выйти. Попробуйте еще раз.', 'error');
    });
}