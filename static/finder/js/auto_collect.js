// auto_collect.js
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
        // Это гарантирует, что мы поймаем клик по любой иконке, даже если она появилась позже
        document.addEventListener('click', (event) => {
            // Проверяем, кликнул ли пользователь по иконке или по родительскому div
            const copyIcon = event.target.closest('.copy_visual_box');
            
            if (copyIcon) {
                console.log('Клик по иконке копирования!');
                // Даем небольшую задержку, чтобы копирование успело выполниться
                setTimeout(() => this.collectAndSend(copyIcon), 300);
            }
        });

        console.log('AutoCollector: слушатель кликов установлен');
    }

    async collectAndSend(iconElement) {
        try {
            console.log('Начинаем сбор данных...');
            
            // Поднимаемся до строки tr (это та строка, где была иконка)
            const row = iconElement.closest('tr');
            if (!row) {
                console.error('Не найдена строка tr');
                return;
            }
            
            console.log('Найдена строка:', row);

            // Ищем ВСЕ колонки с классом data-column для отладки
            const allColumns = row.querySelectorAll('.data-column');
            console.log('Всего колонок с данными:', allColumns.length);
            
            allColumns.forEach((col, index) => {
                console.log(`Колонка ${index + 1}:`, col.textContent.trim());
            });

            // Ищем title - в вашей структуре это колонка с текстом "Винт M 5*10 DIN 965 A4"
            // Это 6-я колонка (индекс 5 в массиве)
            let title = '';
            
            // Способ 1: по nth-child(6)
            const titleByNth = row.querySelector('.data-column:nth-child(6)');
            if (titleByNth) {
                title = titleByNth.textContent.trim();
                console.log('Title найден через nth-child(6):', title);
            }
            
            // Способ 2: по индексу в массиве (6-й элемент, индекс 5)
            if (!title && allColumns.length >= 6) {
                title = allColumns[5].textContent.trim();
                console.log('Title найден по индексу 5:', title);
            }
            
            // Способ 3: ищем ячейку, которая содержит длинный текст с "Винт" или похожие маркеры
            if (!title) {
                for (let col of allColumns) {
                    const text = col.textContent.trim();
                    // Проверяем, похоже ли это на название (содержит буквы, не только цифры)
                    if (text.length > 5 && /[а-яА-Яa-zA-Z]/.test(text) && !text.match(/^\d+$/)) {
                        title = text;
                        console.log('Title найден по содержимому:', title);
                        break;
                    }
                }
            }

            if (!title) {
                console.error('Не удалось найти title в строке');
                this.showNotification('❌ Не найдено название (title)', 'error');
                return;
            }

            // Теперь у нас есть title - это nomenclature_kd
            const nomenclature_kd = title;
            console.log('✅ Номенклатура КД (title):', nomenclature_kd);

            // Находим код (для accounting_code) - это 3-я колонка с "П00121695"
            let code = '';
            
            const codeByNth = row.querySelector('.data-column:nth-child(3)');
            if (codeByNth) {
                code = codeByNth.textContent.trim();
                console.log('Код найден через nth-child(3):', code);
            } else if (allColumns.length >= 3) {
                code = allColumns[2].textContent.trim();
                console.log('Код найден по индексу 2:', code);
            }

            console.log('📦 Бухгалтерский код:', code || 'не найден');

            // Для accounting_name используем тот же title или комбинацию
            const accounting_name = title; // или можно использовать `${code} ${title}`

            // Читаем из буфера обмена
            let clipboardText = '';
            try {
                clipboardText = await navigator.clipboard.readText();
                console.log('📋 Текст из буфера (первые 100 символов):', clipboardText.substring(0, 100));
            } catch (clipboardError) {
                console.error('Ошибка чтения буфера:', clipboardError);
                this.showNotification('❌ Не удалось прочитать буфер обмена', 'error');
                return;
            }

            if (!clipboardText) {
                console.error('Пустой буфер обмена');
                this.showNotification('❌ Буфер обмена пуст', 'error');
                return;
            }

            // Получаем CSRF-токен
            const csrfToken = this.getCsrfToken();
            console.log('🔑 CSRF Token:', csrfToken ? 'Найден' : 'Не найден');

            // Подготавливаем данные для отправки
            const postData = {
                clipboard_text: clipboardText.substring(0, 500),
                accounting_code: code || 'UNKNOWN',
                nomenclature_kd: nomenclature_kd,
                accounting_name: accounting_name
            };
            
            console.log('📤 Отправляем данные на сервер:', postData);

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

            console.log('📥 Статус ответа:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Текст ошибки:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('✅ Результат от сервера:', result);
            
            this.showNotification(
                `✅ Данные сохранены!\n${nomenclature_kd.substring(0, 30)}...`,
                'success'
            );

        } catch (error) {
            console.error('❌ Ошибка в collectAndSend:', error);
            this.showNotification('❌ Ошибка: ' + error.message, 'error');
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

    showNotification(message, type = 'info') {
        const oldNotification = document.querySelector('.auto-collect-notification');
        if (oldNotification) {
            oldNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `auto-collect-notification ${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 350px;
            word-wrap: break-word;
            animation: slideIn 0.3s ease;
        `;

        if (!document.querySelector('#auto-collect-styles')) {
            const style = document.createElement('style');
            style.id = 'auto-collect-styles';
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
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Создаем экземпляр класса после загрузки страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM загружен, инициализация AutoCollector');
        new AutoCollector();
    });
} else {
    console.log('DOM уже загружен, инициализация AutoCollector');
    new AutoCollector();
}