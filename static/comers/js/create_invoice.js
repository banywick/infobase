document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('inputDataForm');
    const ICON_EDIT = "/static/comers/icons/icon_edit.png";
    const ICON_STATUS = "/static/comers/icons/icon_status.png";
    const ICON_DELETE = "/static/comers/icons/icon_delete.png";

    // Функция для отображения ошибок под полями
    function displayErrors(errors) {
        const existingErrors = form.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());

        for (const field in errors) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.style.cssText = `
                    color: #dc3545;
                    font-size: 14px;
                    margin-top: 5px;
                    padding: 5px 10px;
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    animation: fadeIn 0.3s ease;
                `;
                errorElement.textContent = errors[field][0];
                input.after(errorElement);
            }
        }
        
        addAnimationStyles();
    }

    // Функция для отображения информационного сообщения об успехе
    function showSuccessMessage(message = 'Данные успешно сохранены!') {
        const messageElement = document.createElement('div');
        messageElement.className = 'success-message';
        messageElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideInFromRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 300px;
            max-width: 400px;
            backdrop-filter: blur(10px);
        `;
        
        const checkmark = document.createElement('span');
        checkmark.innerHTML = '✓';
        checkmark.style.cssText = `
            background: rgba(255, 255, 255, 0.2);
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
        `;
        
        const textSpan = document.createElement('span');
        textSpan.textContent = message;
        
        messageElement.appendChild(checkmark);
        messageElement.appendChild(textSpan);
        document.body.appendChild(messageElement);
        
        addAnimationStyles();
        
        setTimeout(() => {
            messageElement.style.animation = 'slideOutToRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
            setTimeout(() => messageElement.remove(), 500);
        }, 4000);
        
        messageElement.addEventListener('click', () => {
            messageElement.style.animation = 'slideOutToRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
            setTimeout(() => messageElement.remove(), 500);
        });
        
        return messageElement;
    }

    // Функция для закрытия активного попапа
    function closeActivePopup() {
        const activePopup = document.querySelector('.my-popup.active');
        if (activePopup) {
            activePopup.style.opacity = '0';
            activePopup.style.transform = 'scale(0.95)';
            activePopup.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                activePopup.classList.remove('active');
                setTimeout(() => {
                    activePopup.style.opacity = '';
                    activePopup.style.transform = '';
                    activePopup.style.transition = '';
                }, 50);
                
                form.reset();
                
                const existingErrors = form.querySelectorAll('.error-message');
                existingErrors.forEach(error => error.remove());
            }, 300);
        }
    }

    // Функция добавления CSS стилей для анимаций
    function addAnimationStyles() {
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
            `;
            document.head.appendChild(style);
        }
    }

    // Функция для создания строки таблицы (такая же как в другом модуле!)
    function createTableRow(item) {
        const row = document.createElement('tr');
        
        // Извлекаем текстовые значения из вложенных объектов (ТОЧНО ТАК ЖЕ!)
        const commentText = item.comment ? item.comment.text : '';
        const leadingName = item.leading ? item.leading.name : '';
        const specialistName = item.specialist ? item.specialist.name : '';
        const statusName = item.status ? item.status.name : '';
        const supplierName = item.supplier ? item.supplier.name : '';

        row.innerHTML = `
            <td class="invoice-number">${item.invoice_number || ''}</td>
            <td class="date-cell">${item.date || ''}</td>
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
            <td class="status-cell">${item.description || ''}</td>
            <td>
                <div class="action_cell_table">
                    <div class="edit_invoice_button">
                        <img src="${ICON_EDIT}" alt="Редактировать">
                        <div class="open-btn" data-popup="popup5">Редактировать</div>
                    </div>
                    <div class="edit_invoice_button">
                        <img src="${ICON_STATUS}" alt="Статус">
                        <div class="open-btn" data-popup="popup6">Статус</div>
                    </div>
                    <div class="edit_invoice_button" data-id="${item.id}">
                        <img src="${ICON_DELETE}" alt="Удалить">
                        <div class="open-btn" data-popup="popup7">Удалить</div>
                    </div>
                </div>
            </td>
        `;
        
        console.log('Создана строка с данными:', {
            id: item.id,
            invoice_number: item.invoice_number,
            supplierName,
            specialistName,
            leadingName,
            statusName,
            commentText
        });
        
        return row;
    }

    // Функция добавления новой строки в таблицу
    function addNewRowToTable(item) {
        const tableBody = document.getElementById('invoiceTableBody');
        if (!tableBody) {
            console.error('Элемент invoiceTableBody не найден');
            return;
        }
        
        const newRow = createTableRow(item);
        
        // Добавляем строку в начало таблицы
        if (tableBody.firstChild) {
            tableBody.insertBefore(newRow, tableBody.firstChild);
        } else {
            tableBody.appendChild(newRow);
        }
        
        // Анимация появления
        animateNewRow(newRow);
        
        // Обновляем обработчики событий
        bindPopupEventsToRow(newRow);
        
        console.log('Добавлена новая строка с ID:', item.id);
        
        return newRow;
    }

    // Функция анимации появления новой строки
    function animateNewRow(row) {
        if (!row) return;
        
        row.style.opacity = '0';
        row.style.transform = 'translateY(-20px)';
        row.style.backgroundColor = '#e8f5e9';
        row.style.transition = 'all 0.5s ease';
        
        requestAnimationFrame(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        });
        
        setTimeout(() => {
            row.style.transition = 'background-color 1.5s ease';
            row.style.backgroundColor = '';
        }, 3000);
        
        setTimeout(() => {
            row.style.transition = '';
        }, 5000);
    }

    // Функция привязки обработчиков событий для попапов
    function bindPopupEventsToRow(row) {
        const editButtons = row.querySelectorAll('.edit_invoice_button .open-btn');
        editButtons.forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', function(e) {
                const popupId = this.getAttribute('data-popup');
                if (popupId && window.openPopup) {
                    window.openPopup(popupId);
                    
                    // Для кнопки удаления сохраняем ID
                    if (popupId === 'popup7') {
                        const dataId = this.closest('.edit_invoice_button').getAttribute('data-id');
                        window.currentDeleteId = dataId;
                        console.log('Установлен ID для удаления:', dataId);
                    }
                }
            });
        });
    }

    // Главный обработчик отправки формы
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);

        console.log('Отправка формы с данными:');
        for (let [key, value] of formData.entries()) {
            console.log(key + ':', value);
        }

        // Показываем индикатор загрузки
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton ? submitButton.textContent : '';
        
        if (submitButton) {
            submitButton.textContent = 'Сохранение...';
            submitButton.disabled = true;
            submitButton.style.opacity = '0.7';
        }

        fetch('/comers/add_invoice_data/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errors => {
                    throw errors;
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Успешный ответ от сервера:', data);
            
            if (data.success && data.data) {
                const createdItem = data.data;
                
                // ДЕБАГ: Проверяем структуру данных
                console.log('Структура createdItem:', {
                    id: createdItem.id,
                    hasCommentObject: !!createdItem.comment,
                    commentIsObject: typeof createdItem.comment === 'object',
                    commentText: createdItem.comment ? createdItem.comment.text : 'нет комментария',
                    hasSupplierObject: !!createdItem.supplier,
                    supplierName: createdItem.supplier ? createdItem.supplier.name : 'нет поставщика'
                });
                
                // Показываем сообщение об успехе
                showSuccessMessage('Данные успешно сохранены!');
                
                // Добавляем новую строку в таблицу
                addNewRowToTable(createdItem);
                
                // Закрываем попап
                setTimeout(() => {
                    closeActivePopup();
                }, 1000);
                
                // Если сервер вернул только ID связанных объектов, делаем доп. запрос
                if (createdItem.comment && typeof createdItem.comment === 'number' ||
                    createdItem.supplier && typeof createdItem.supplier === 'number') {
                    enhanceRowWithFullData(createdItem.id);
                }
            } else {
                throw new Error('Не удалось сохранить данные');
            }
        })
        .catch(errors => {
            console.error('Ошибки при отправке формы:', errors);
            
            // Восстанавливаем кнопку
            if (submitButton) {
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                submitButton.style.opacity = '';
            }
            
            if (errors && typeof errors === 'object') {
                displayErrors(errors);
                
                // Показываем сообщение об ошибке
                showNotification('Ошибка при сохранении данных', 'error');
            }
        })
        .finally(() => {
            if (submitButton && submitButton.disabled) {
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                submitButton.style.opacity = '';
            }
        });
    });

    // Функция для получения полных данных если сервер вернул только ID
    function enhanceRowWithFullData(itemId) {
        console.log('Запрашиваю полные данные для ID:', itemId);
        
        fetch(`/comers/get_position/${itemId}/`)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка получения данных');
                return response.json();
            })
            .then(fullData => {
                console.log('Получены полные данные:', fullData);
                
                // Находим строку с этим ID
                const row = document.querySelector(`tr .edit_invoice_button[data-id="${itemId}"]`)?.closest('tr');
                if (row) {
                    // Обновляем ячейки с вложенными объектами
                    if (fullData.comment && fullData.comment.text) {
                        const commentCell = row.querySelector('.comment-cell');
                        if (commentCell) commentCell.textContent = fullData.comment.text;
                    }
                    
                    if (fullData.supplier && fullData.supplier.name) {
                        const supplierCell = row.querySelector('.supplier-cell');
                        if (supplierCell) supplierCell.textContent = fullData.supplier.name;
                    }
                    
                    if (fullData.specialist && fullData.specialist.name) {
                        const specialistCell = row.querySelector('td:nth-child(11)'); // 11-я ячейка
                        if (specialistCell) specialistCell.textContent = fullData.specialist.name;
                    }
                    
                    if (fullData.leading && fullData.leading.name) {
                        const leadingCell = row.querySelector('td:nth-child(12)'); // 12-я ячейка
                        if (leadingCell) leadingCell.textContent = fullData.leading.name;
                    }
                    
                    if (fullData.status && fullData.status.name) {
                        const statusCell = row.querySelector('.status-cell');
                        if (statusCell) statusCell.textContent = fullData.status.name;
                    }
                    
                    console.log('Строка обновлена полными данными');
                }
            })
            .catch(error => {
                console.error('Ошибка при получении полных данных:', error);
            });
    }

    // Функция showNotification (если не определена)
    if (typeof window.showNotification === 'undefined') {
        window.showNotification = function(message, type = 'info') {
            console.log(`[${type.toUpperCase()}] ${message}`);
            
            const notification = document.createElement('div');
            notification.className = 'simple-notification';
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                background: ${type === 'success' ? '#4CAF50' : 
                             type === 'error' ? '#f44336' : 
                             type === 'warning' ? '#ff9800' : '#2196F3'};
                color: white;
                border-radius: 4px;
                z-index: 10000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                font-family: Arial, sans-serif;
                font-size: 14px;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        };
    }

    // Инициализация
    addAnimationStyles();
});