document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.querySelector('.send_data_form_edit_status_button');
    const form = document.getElementById('editInvoiceFormStatus');
    
    if (sendButton && form) {
        sendButton.addEventListener('click', async function(event) {
            event.preventDefault();
            
            try {
                // Собираем данные формы
                const formData = new FormData(form);
                const data = {};
                
                // Преобразуем FormData в обычный объект
                formData.forEach((value, key) => {
                    // Пропускаем csrfmiddlewaretoken - он в заголовках
                    if (key !== 'csrfmiddlewaretoken') {
                        data[key] = value;
                    }
                });
                
                // Получаем ID инвойса из кнопки редактирования статуса
                // Ищем ближайшую кнопку редактирования статуса
                const editStatusButton = document.querySelector('.edit_status_button[data-action="status"]');
                const invoiceId = editStatusButton ? editStatusButton.getAttribute('data-id') : null;
                
                if (!invoiceId) {
                    alert('❌ Не найден ID инвойса');
                    return;
                }
                
                // Получаем CSRF токен
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // URL для обновления статуса конкретного инвойса
                // Если endpoint для обновления: /comers/edit_invoices/<id>/
                const url = `/comers/edit_invoices/${invoiceId}/`;
                
                const response = await fetch(url, {
                    method: 'PATCH', // Используем PATCH для частичного обновления
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        status: data.status,
                        description: data.description
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ Статус успешно обновлен!');
                    
                    // Обновляем статус на странице без перезагрузки (опционально)
                    const statusCell = editStatusButton.closest('tr').querySelector('.status-cell');
                    if (statusCell) {
                        // Находим выбранный текст статуса
                        const select = form.querySelector('#id_status');
                        const selectedOption = select.options[select.selectedIndex];
                        statusCell.textContent = selectedOption.textContent;
                    }
                    
                    // Закрываем попап, если он есть
                    const popup = document.getElementById('popup6');
                    if (popup) {
                        popup.style.display = 'none';
                    }
                    
                } else {
                    // Показываем ошибки валидации
                    let errorMessage = 'Ошибки при обновлении статуса:\n';
                    for (const field in result.errors) {
                        if (Array.isArray(result.errors[field])) {
                            errorMessage += `${field}: ${result.errors[field].join(', ')}\n`;
                        } else {
                            errorMessage += `${field}: ${result.errors[field]}\n`;
                        }
                    }
                    alert(errorMessage || 'Неизвестная ошибка');
                }
                
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных');
            }
        });
    }
});