document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.querySelector('.send_data_form_edit_button');
    const form = document.getElementById('editInvoiceForm');
    
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
                        // Обрабатываем множественные поля
                        if (data[key]) {
                            if (Array.isArray(data[key])) {
                                data[key].push(value);
                            } else {
                                data[key] = [data[key], value];
                            }
                        } else {
                            data[key] = value;
                        }
                    }
                });
                
                // Получаем ID инвойса (предполагаем, что он в скрытом поле)
                const invoiceId = data.invoice_id;
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // URL для обновления конкретного инвойса
                // Если endpoint для обновления: /comers/edit_invoices/<id>/
                const url = `/comers/edit_invoices/${invoiceId}/`;
                
                const response = await fetch(url, {
                    method: 'PATCH', // Используем PATCH для частичного обновления
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ Данные успешно обновлены!');
                    // Можно добавить редирект или обновление интерфейса
                    // window.location.href = '/comers/invoices/'; // например
                } else {
                    // Показываем ошибки валидации
                    let errorMessage = 'Ошибки при обновлении:\n';
                    for (const field in result.errors) {
                        errorMessage += `${field}: ${result.errors[field].join(', ')}\n`;
                    }
                    alert(errorMessage);
                }
                
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных');
            }
        });
    }
});