// auto_collect.js - версия без уведомлений
class AutoCollector {
    constructor() {
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupListeners());
        } else {
            this.setupListeners();
        }
    }

    setupListeners() {
        // Используем делегирование событий на весь документ
        document.addEventListener('click', (event) => {
            // Проверяем, кликнул ли пользователь по иконке копирования
            const copyIcon = event.target.closest('.copy_visual_box');
            
            if (copyIcon) {
                // Даем небольшую задержку, чтобы копирование успело выполниться
                setTimeout(() => this.collectAndSend(), 300);
            }
        });
    }

    async collectAndSend() {
        try {
            // 1. Получаем значение из элемента kd_title
            const kdTitleElement = document.getElementById('kd_title');
            if (!kdTitleElement) {
                console.error('Элемент с id="kd_title" не найден');
                return;
            }

            const nomenclature_kd = kdTitleElement.textContent.trim();

            if (!nomenclature_kd) {
                console.error('Элемент kd_title пуст');
                return;
            }

            // 2. Читаем из буфера обмена
            let clipboardText = '';
            try {
                clipboardText = await navigator.clipboard.readText();
            } catch (clipboardError) {
                console.error('Ошибка чтения буфера:', clipboardError);
                return;
            }

            if (!clipboardText) {
                console.error('Пустой буфер обмена');
                return;
            }

            // Извлекаем бухгалтерский код из текста буфера (первая часть до табуляции или пробела)
            const parts = clipboardText.split(/\t|\s+/);
            const accounting_code = parts[0] || 'UNKNOWN';
            
            // Для accounting_name берем ВСЁ, КРОМЕ первого кода
            let accounting_name = '';
            if (parts.length > 1) {
                accounting_name = parts.slice(1).join(' ').trim();
            } else {
                accounting_name = clipboardText.trim();
            }

            if (!accounting_name) {
                accounting_name = clipboardText.trim();
            }

            // Получаем CSRF-токен
            const csrfToken = this.getCsrfToken();

            // Подготавливаем данные для отправки
            const postData = {
                clipboard_text: clipboardText.substring(0, 500),
                accounting_code: accounting_code,
                nomenclature_kd: nomenclature_kd,
                accounting_name: accounting_name
            };

            // Отправляем на сервер
            const response = await fetch('/finder/comparison/auto-collect/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(postData),
                credentials: 'include',
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Ошибка ответа:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Данные успешно сохранены:', result);

        } catch (error) {
            console.error('Ошибка в collectAndSend:', error);
        }
    }

    getCsrfToken() {
        // Ищем в cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Ищем в meta тегах
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        // Пробуем найти токен в форме
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
}

// Создаем экземпляр класса после загрузки страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AutoCollector();
    });
} else {
    new AutoCollector();
}