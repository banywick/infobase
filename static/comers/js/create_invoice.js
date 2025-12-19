// static/comers/js/create_invoice.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    const form = document.getElementById('createInvoiceForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton ? submitButton.textContent : '';
        
        // Показываем индикатор загрузки
        if (submitButton) {
            submitButton.textContent = 'Сохранение...';
            submitButton.disabled = true;
        }
        
        try {
            const formData = new FormData(form);
            
            const response = await fetch('/comers/add_invoice_data/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': ComersApp.getCsrfToken(),
                },
                body: formData,
            });
            
            const data = await response.json();
            
            if (data.success && data.data) {
                ComersApp.showNotification('Данные успешно сохранены!', 'success');
                
                // Добавляем новую строку В НИЗ таблицы
                ComersApp.addRowToTable(data.data, 'bottom');
                
                // Закрываем попап
                setTimeout(() => {
                    ComersApp.closeActivePopup();
                    form.reset();
                }, 1000);
                
            } else {
                throw data.errors || { __all__: ['Не удалось сохранить данные'] };
            }
            
        } catch (errors) {
            console.error('Ошибки при отправке формы:', errors);
            ComersApp.displayFormErrors('createInvoiceForm', errors);
            ComersApp.showNotification('Ошибка при сохранении данных', 'error');
            
        } finally {
            // Восстанавливаем кнопку
            if (submitButton) {
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
            }
        }
    });
});