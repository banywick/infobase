// static/comers/js/create_supplier.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    const form = document.getElementById('add_suppler_form');
    const submitBtn = form?.querySelector('button.button_supplier');
    if (!form || !submitBtn) return;
    
    submitBtn.addEventListener('click', async function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        // Очищаем ошибки
        ComersApp.clearFormErrors('add_suppler_form');
        
        // Валидация обязательных полей
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.style.cssText = `
                    color: #dc3545;
                    font-size: 12px;
                    margin-top: 5px;
                `;
                errorElement.textContent = 'Это поле обязательно для заполнения';
                field.after(errorElement);
            }
        });
        
        if (!isValid) {
            ComersApp.showNotification('Заполните все обязательные поля', 'error');
            return;
        }
        
        // Показываем индикатор загрузки
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(form);
            
            const response = await fetch('/comers/add_supplier/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': ComersApp.getCsrfToken(),
                },
            });
            
            if (response.ok) {
                ComersApp.showNotification('Поставщик успешно добавлен', 'success');
                
                // Обновляем данные без перезагрузки
                await ComersApp.loadAllData();
                
                // Закрываем попап и очищаем форму
                setTimeout(() => {
                    ComersApp.closeActivePopup();
                    form.reset();
                }, 1500);
                
            } else {
                const errors = await response.json();
                throw errors;
            }
            
        } catch (errors) {
            ComersApp.displayFormErrors('add_suppler_form', errors);
            ComersApp.showNotification('Исправьте ошибки в форме', 'error');
            
        } finally {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });
});