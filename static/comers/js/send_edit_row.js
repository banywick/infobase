// static/comers/js/send_edit_row.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    const sendButton = document.querySelector('.send_data_form_edit_button');
    
    if (sendButton) {
        sendButton.addEventListener('click', async function(event) {
            event.preventDefault();
            
            const form = document.getElementById('editInvoiceForm');
            if (!form) {
                console.error('Форма редактирования не найдена');
                return;
            }
            
            const currentEditId = ComersApp.getCurrentEditId();
            if (!currentEditId) {
                ComersApp.showNotification('ID для редактирования не найден', 'error');
                return;
            }
            
            // Показываем индикатор загрузки
            const originalText = sendButton.textContent;
            sendButton.textContent = 'Сохранение...';
            sendButton.disabled = true;
            
            try {
                // Собираем данные формы
                const formData = new FormData(form);
                const data = {};
                
                formData.forEach((value, key) => {
                    if (key !== 'csrfmiddlewaretoken') {
                        data[key] = value;
                    }
                });
                
                console.log('Отправка данных для редактирования:', data);
                
                // Отправляем запрос на обновление через правильный эндпоинт
                const response = await fetch(`/comers/edit_invoices/${currentEditId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': ComersApp.getCsrfToken(),
                    },
                    body: JSON.stringify(data),
                });
                
                const result = await response.json();
                console.log('Ответ сервера:', result);
                
                if (response.ok && result.success) {
                    ComersApp.showNotification('✅ Данные успешно обновлены!', 'success');
                    
                    // Обновляем строку в таблице
                    if (result.data) {
                        ComersApp.updateRowInTable(result.data);
                    } else {
                        // Если сервер не вернул данные, перезагружаем все данные
                        await ComersApp.loadAllData();
                    }
                    
                    // Закрываем попап
                    ComersApp.closeActivePopup();
                    
                } else {
                    // Показываем ошибки валидации
                    const errors = result.errors || { __all__: ['Ошибка обновления'] };
                    ComersApp.displayFormErrors('editInvoiceForm', errors);
                    ComersApp.showNotification('Ошибка при обновлении данных', 'error');
                }
                
            } catch (error) {
                console.error('Ошибка:', error);
                ComersApp.showNotification('Произошла ошибка при отправке данных', 'error');
                
            } finally {
                // Восстанавливаем кнопку
                sendButton.textContent = originalText;
                sendButton.disabled = false;
            }
        });
    }
    
    // Также обрабатываем отправку формы по Enter
    const form = document.getElementById('editInvoiceForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            if (sendButton) sendButton.click();
        });
    }
});