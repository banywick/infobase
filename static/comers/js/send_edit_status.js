// static/comers/js/send_edit_status.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    const statusSubmitButton = document.querySelector('.send_data_form_edit_status_button');
    if (statusSubmitButton) {
        statusSubmitButton.addEventListener('click', async function() {
            const form = document.getElementById('editInvoiceFormStatus');
            if (!form) return;
            
            const currentEditId = ComersApp.getCurrentEditId();
            if (!currentEditId) {
                ComersApp.showNotification('ID для изменения статуса не найден', 'error');
                return;
            }
            
            // Показываем индикатор загрузки
            const originalText = statusSubmitButton.textContent;
            statusSubmitButton.textContent = 'Сохранение...';
            statusSubmitButton.disabled = true;
            
            try {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                console.log('Отправка данных статуса:', data);
                
                // Отправляем запрос на обновление статуса
                const response = await fetch(`/comers/edit_invoices/${currentEditId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': ComersApp.getCsrfToken(),
                    },
                    body: JSON.stringify({
                        status: data.status,
                        description: data.description
                    }),
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    ComersApp.showNotification('✅ Статус успешно обновлен!', 'success');
                    
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
                    const errors = result.errors || { __all__: ['Ошибка обновления статуса'] };
                    ComersApp.displayFormErrors('editInvoiceFormStatus', errors);
                    ComersApp.showNotification('Ошибка при обновлении статуса', 'error');
                }
                
            } catch (error) {
                console.error('Ошибка:', error);
                ComersApp.showNotification('Произошла ошибка при отправке данных', 'error');
                
            } finally {
                // Восстанавливаем кнопку
                statusSubmitButton.textContent = originalText;
                statusSubmitButton.disabled = false;
            }
        });
    }
});