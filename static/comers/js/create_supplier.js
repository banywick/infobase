document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add_suppler_form');
    const submitBtn = form.querySelector('button.button_supplier');
    let hasErrors = false;
    
    // Функция для очистки ошибок
    function clearErrors() {
        hasErrors = false;
        const existingErrors = form.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());
    }
    
    // Функция для отображения ошибок
    function displayErrors(errors) {
        hasErrors = true;
        
        // Сохраняем ошибки в localStorage для восстановления при повторном открытии
        saveErrorsToStorage(errors);
        
        const existingErrors = form.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());

        for (const field in errors) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.style.color = 'red';
                errorElement.style.fontSize = '12px';
                errorElement.style.marginTop = '5px';
                errorElement.textContent = errors[field][0];
                input.after(errorElement);
            }
        }
    }
    
    // Функция для сохранения ошибок в localStorage
    function saveErrorsToStorage(errors) {
        if (errors && typeof errors === 'object') {
            localStorage.setItem('supplier_form_errors', JSON.stringify(errors));
            localStorage.setItem('supplier_form_has_errors', 'true');
        }
    }
    
    // Функция для восстановления ошибок из localStorage
    function restoreErrorsFromStorage() {
        const errorsJson = localStorage.getItem('supplier_form_errors');
        const hasErrorsFlag = localStorage.getItem('supplier_form_has_errors');
        
        if (errorsJson && hasErrorsFlag === 'true') {
            try {
                const errors = JSON.parse(errorsJson);
                displayErrors(errors);
                return true;
            } catch (e) {
                console.error('Ошибка при восстановлении ошибок:', e);
                clearErrorsStorage();
            }
        }
        return false;
    }
    
    // Функция для очистки ошибок в localStorage
    function clearErrorsStorage() {
        localStorage.removeItem('supplier_form_errors');
        localStorage.removeItem('supplier_form_has_errors');
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
            max-width: 400px;
            word-wrap: break-word;
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
    
    // Вешаем обработчик на кнопку вместо формы
    submitBtn.addEventListener('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        // Очищаем предыдущие ошибки перед отправкой
        clearErrors();
        clearErrorsStorage();
        
        const formData = new FormData(form);
        
        // Валидация полей перед отправкой
        let isValid = true;
        form.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.style.color = 'red';
                errorElement.style.fontSize = '12px';
                errorElement.style.marginTop = '5px';
                errorElement.textContent = 'Это поле обязательно для заполнения';
                field.after(errorElement);
                
                // Сохраняем эту ошибку
                if (!window.formErrors) window.formErrors = {};
                window.formErrors[field.name] = ['Это поле обязательно для заполнения'];
                saveErrorsToStorage(window.formErrors);
            }
        });
        
        if (!isValid) {
            showNotification('Заполните все обязательные поля', 'error');
            return;
        }
        
        // Показываем индикатор загрузки
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;
        
        fetch('/comers/add_supplier/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
            
            if (response.ok) {
                // Показываем уведомление об успехе
                showNotification('Поставщик успешно добавлен', 'success');
                
                // Очищаем ошибки из хранилища
                clearErrorsStorage();
                
                // Закрываем попап через небольшой таймаут
                setTimeout(() => {
                    const popup = form.closest('.my-popup');
                    if (popup) {
                        popup.classList.remove('active');
                    }
                    // Очищаем форму
                    form.reset();
                    // Перезагружаем страницу
                    window.location.reload();
                }, 1500);
            } else {
                return response.json().then(errors => {
                    throw errors;
                });
            }
        })
        .catch(errors => {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
            
            console.error('Ошибки:', errors);
            if (errors && typeof errors === 'object') {
                displayErrors(errors);
                showNotification('Исправьте ошибки в форме', 'error');
            } else {
                showNotification('Произошла неизвестная ошибка', 'error');
            }
        });
    });
    
    // Обработчик submit для формы на случай отправки через Enter
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        submitBtn.click();
    });
    
    // БЛОКИРОВКА ЗАКРЫТИЯ ДЛЯ POPUP2
    const popup = document.getElementById('popup2');
    if (popup) {
        // Перехватываем клик на фон попапа
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                // Проверяем есть ли ошибки перед закрытием
                const errorMessages = form.querySelectorAll('.error-message');
                if (errorMessages.length > 0) {
                    e.stopPropagation();
                    e.preventDefault();
                    showNotification('Исправьте ошибки перед закрытием', 'error');
                    return;
                }
                // Если ошибок нет, закрываем попап и очищаем форму
                popup.classList.remove('active');
                form.reset();
                clearErrorsStorage();
            }
        });
        
        // Перехватываем клик на крестик
        const closeBtn = popup.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                const errorMessages = form.querySelectorAll('.error-message');
                if (errorMessages.length > 0) {
                    e.stopPropagation();
                    e.preventDefault();
                    showNotification('Исправьте ошибки перед закрытием', 'error');
                    return false;
                }
                popup.classList.remove('active');
                form.reset();
                clearErrorsStorage();
                return true;
            });
        }
    }
    
    // Перехватываем нажатие ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activePopup = document.querySelector('.my-popup.active');
            if (activePopup && activePopup.id === 'popup2') {
                const errorMessages = form.querySelectorAll('.error-message');
                if (errorMessages.length > 0) {
                    e.stopPropagation();
                    e.preventDefault();
                    showNotification('Исправьте ошибки перед закрытием', 'error');
                    return;
                }
            }
        }
    });
    
    // Восстанавливаем ошибки при открытии попапа
    // function restoreFormState() {
    //     // Восстанавливаем значения полей если они были сохранены
    //     const savedData = localStorage.getItem('supplier_form_data');
    //     if (savedData) {
    //         try {
    //             const data = JSON.parse(savedData);
    //             for (const field in data) {
    //                 const input = form.querySelector(`[name="${field}"]`);
    //                 if (input) {
    //                     input.value = data[field];
    //                 }
    //             }
    //         } catch (e) {
    //             console.error('Ошибка при восстановлении данных формы:', e);
    //         }
    //     }
        
    //     // Восстанавливаем ошибки
    //     restoreErrorsFromStorage();
    // }
    
    // Сохраняем данные формы при изменении
    form.addEventListener('input', function(e) {
        const fieldName = e.target.name;
        const fieldValue = e.target.value;
        
        // Сохраняем данные формы
        const formData = {};
        new FormData(form).forEach((value, key) => {
            formData[key] = value;
        });
        
        localStorage.setItem('supplier_form_data', JSON.stringify(formData));
        
        // Если пользователь исправляет поле с ошибкой, убираем эту ошибку
        const errorMessages = form.querySelectorAll('.error-message');
        if (errorMessages.length > 0) {
            // Находим ошибку для этого поля и удаляем ее
            const fieldError = document.querySelector(`[name="${fieldName}"] + .error-message`);
            if (fieldError) {
                fieldError.remove();
                
                // Обновляем ошибки в localStorage
                const errorsJson = localStorage.getItem('supplier_form_errors');
                if (errorsJson) {
                    try {
                        const errors = JSON.parse(errorsJson);
                        delete errors[fieldName];
                        
                        if (Object.keys(errors).length === 0) {
                            clearErrorsStorage();
                        } else {
                            localStorage.setItem('supplier_form_errors', JSON.stringify(errors));
                        }
                    } catch (e) {
                        console.error('Ошибка при обновлении ошибок:', e);
                    }
                }
            }
        }
    });
    
    // Обработчик для открытия попапа
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('open-btn')) {
            const popupId = e.target.getAttribute('data-popup');
            if (popupId === 'popup2') {
                // Восстанавливаем состояние формы после небольшой задержки
                setTimeout(restoreFormState, 100);
            }
        }
    });
    
    // Восстанавливаем состояние при загрузке страницы, если попап уже открыт
    if (popup && popup.classList.contains('active')) {
        setTimeout(restoreFormState, 100);
    }
    
    // Очищаем сохраненные данные при успешной отправке
    form.addEventListener('submit', function() {
        localStorage.removeItem('supplier_form_data');
    });
});