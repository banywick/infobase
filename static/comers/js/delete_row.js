document.addEventListener('DOMContentLoaded', function() {
    let currentDeleteId = null;
    
    // Сохраняем ID при клике на кнопку удаления
    document.addEventListener('click', function(e) {
        // Находим кнопку удаления, на которую кликнули
        const deleteBtn = e.target.closest('.edit_invoice_button[data-id]');
        if (deleteBtn && deleteBtn.querySelector('.open-btn[data-popup="popup7"]')) {
            currentDeleteId = deleteBtn.getAttribute('data-id');
            console.log('ID для удаления сохранен:', currentDeleteId);
            
            // Также можно сохранить порядковый номер для обновления
            const row = deleteBtn.closest('tr');
            const sequentialId = row.querySelector('.id-cell')?.textContent;
            console.log('Порядковый номер:', sequentialId);
        }
    });
    
    // Обработчик для кнопки удаления в попапе
    document.getElementById('del_row_comers_table').addEventListener('click', function() {
        if (!currentDeleteId) {
            console.error('ID для удаления не найден');
            return;
        }
        
        const deleteButton = this;
        const originalText = deleteButton.textContent;
        
        // Показываем индикатор загрузки
        deleteButton.textContent = 'Удаление...';
        deleteButton.disabled = true;
        
        // Отправляем запрос на удаление
        fetch(`/comers/remove_position/${currentDeleteId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Позиция удалена:', data);
            
            // НАХОДИМ СТРОКУ ПО data-id КНОПКИ УДАЛЕНИЯ - ЭТО ПРАВИЛЬНЫЙ ПУТЬ
            const rowToDelete = document.querySelector(`tr .edit_invoice_button[data-id="${currentDeleteId}"]`)?.closest('tr');
            
            if (rowToDelete) {
                // Добавляем анимацию удаления
                rowToDelete.style.transition = 'all 0.3s ease';
                rowToDelete.style.opacity = '0';
                rowToDelete.style.transform = 'translateX(-100%)';
                
                setTimeout(() => {
                    rowToDelete.remove();
                    console.log('Строка удалена из DOM');
                    
                    // Обновляем порядковые номера ВСЕХ строк
                    updateSequentialNumbers();
                }, 300);
            } else {
                console.warn('Строка для удаления не найдена в DOM');
                // Попробуем альтернативный поиск
                const altRowToDelete = document.querySelector(`tr .id-cell:contains("${currentDeleteId}")`)?.closest('tr');
                if (altRowToDelete) {
                    altRowToDelete.remove();
                    updateSequentialNumbers();
                }
            }
            
            // Закрываем попап
            const activePopup = document.querySelector('.my-popup.active');
            if (activePopup) {
                activePopup.classList.remove('active');
                
                // Альтернативный вариант: имитируем клик на крестик
                const closeBtn = activePopup.querySelector('.close-btn');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
            
            // Показываем уведомление об успехе
            showNotification('Позиция успешно удалена', 'success');
        })
        .catch(error => {
            console.error('Ошибка при удалении:', error);
            showNotification('Ошибка при удалении: ' + error.message, 'error');
        })
        .finally(() => {
            // Восстанавливаем кнопку
            deleteButton.textContent = originalText;
            deleteButton.disabled = false;
            currentDeleteId = null;
        });
    });
    
    // Функция для получения CSRF токена
    function getCsrfToken() {
        // Вариант 1: из cookie (Django по умолчанию)
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
            
        // Вариант 2: из meta-тега
        if (!cookieValue) {
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                return metaToken.getAttribute('content');
            }
        }
        
        // Вариант 3: из скрытого input
        if (!cookieValue) {
            const inputToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (inputToken) {
                return inputToken.value;
            }
        }
        
        return cookieValue || '';
    }
    
    // Функция для обновления порядковых номеров после удаления
    function updateSequentialNumbers() {
        const tableBody = document.getElementById('invoiceTableBody');
        if (!tableBody) {
            console.warn('Таблица invoiceTableBody не найдена');
            return;
        }
        
        const rows = tableBody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            const idCell = row.querySelector('.id-cell');
            if (idCell) {
                idCell.textContent = index + 1; // Обновляем порядковый номер
            }
        });
        
        console.log(`Порядковые номера обновлены. Всего строк: ${rows.length}`);
    }
    
    // Функция показа уведомлений
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            font-family: Arial, sans-serif;
        `;
        
        document.body.appendChild(notification);
        
        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
        
        // Добавляем CSS анимации если их нет
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Обработчик для кнопки "Отменить" в попапе
    const cancelBtn = document.querySelector('.popup-content .button--green');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            const activePopup = document.querySelector('.my-popup.active');
            if (activePopup) {
                activePopup.classList.remove('active');
                currentDeleteId = null;
            }
        });
    }
    
    // Добавляем вспомогательную функцию для поиска по тексту (если нужно)
    if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                    Element.prototype.webkitMatchesSelector;
    }
    
    if (!Element.prototype.closest) {
        Element.prototype.closest = function(s) {
            var el = this;
            if (!document.documentElement.contains(el)) return null;
            do {
                if (el.matches(s)) return el;
                el = el.parentElement || el.parentNode;
            } while (el !== null && el.nodeType === 1); 
            return null;
        };
    }
});