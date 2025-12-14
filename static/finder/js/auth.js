// Элементы DOM
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const serverError = document.getElementById('serverError');
const successMessage = document.getElementById('successMessage');
const loginButton = document.getElementById('loginButton');

// Флаг валидности формы
let isFormValid = false;

// Валидация формы
function validateForm() {
    let isValid = true;
    
    // Сброс ошибок
    usernameError.style.display = 'none';
    passwordError.style.display = 'none';
    usernameInput.classList.remove('error');
    passwordInput.classList.remove('error');
    
    // Валидация логина
    if (!usernameInput.value.trim()) {
        usernameError.textContent = 'Пожалуйста, введите логин';
        usernameError.style.display = 'block';
        usernameInput.classList.add('error');
        isValid = false;
    }
    
    // Валидация пароля
    if (!passwordInput.value.trim()) {
        passwordError.textContent = 'Пожалуйста, введите пароль';
        passwordError.style.display = 'block';
        passwordInput.classList.add('error');
        isValid = false;
    }
    
    isFormValid = isValid;
    return isValid;
}

// Обработчики событий для live-валидации
usernameInput.addEventListener('blur', validateForm);
passwordInput.addEventListener('blur', validateForm);

// Обработчик для Enter в форме
loginForm.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        submitLogin();
    }
});

// Функция отправки формы
async function submitLogin() {
    // Скрываем предыдущие сообщения
    serverError.classList.remove('show');
    successMessage.classList.remove('show');
    
    // Валидируем форму
    if (!validateForm()) {
        return;
    }
    
    // Собираем данные формы
    const formData = {
        username: usernameInput.value.trim(),
        password: passwordInput.value
    };
    
    // Блокируем кнопку и показываем индикатор загрузки
    loginButton.disabled = true;
    loginButton.innerHTML = '<span class="loading"></span>Выполняется вход...';
    
    try {
        // Отправляем POST запрос на сервер
        const response = await fetch('/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Для Django CSRF защиты
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        // Сбрасываем состояние кнопки
        loginButton.disabled = false;
        loginButton.textContent = 'Войти';
        
        if (response.ok) {
            // Успешная авторизация
            successMessage.classList.add('show');
            
            // Сохраняем данные пользователя (например, токен или информацию о пользователе)
            if (data) {
                localStorage.setItem('userData', JSON.stringify(data));
            }
            
            // Перенаправление через 2 секунды
            setTimeout(() => {
                window.location.href = '/'; // Замените на нужный URL
            }, 2000);
            
        } else {
            // Ошибка авторизации
            const errorMessage = data.error || 'Неверный логин или пароль';
            serverError.textContent = errorMessage;
            serverError.classList.add('show');
            
            // Анимация ошибки
            serverError.style.animation = 'none';
            setTimeout(() => {
                serverError.style.animation = 'fadeIn 0.3s ease';
            }, 10);
        }
        
    } catch (error) {
        // Сетевая ошибка
        console.error('Ошибка сети:', error);
        serverError.textContent = 'Ошибка соединения с сервером. Проверьте подключение к интернету.';
        serverError.classList.add('show');
        
        // Сбрасываем состояние кнопки
        loginButton.disabled = false;
        loginButton.textContent = 'Войти';
    }
}

// Функция для получения CSRF токена (для Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Инициализация формы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли сохраненный логин
    const savedUserData = localStorage.getItem('userData');
    if (savedUserData) {
        try {
            const userData = JSON.parse(savedUserData);
            if (userData.username) {
                usernameInput.value = userData.username;
            }
        } catch (e) {
            console.error('Ошибка при чтении сохраненных данных:', e);
        }
    }
    
    // Фокус на поле логина при загрузке
    usernameInput.focus();
});