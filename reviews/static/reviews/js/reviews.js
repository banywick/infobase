document.getElementById('reviews_form').addEventListener('submit', async function(e) {
    e.preventDefault(); // Предотвращаем перезагрузку страницы
    
    const submitBtn = document.getElementById('submit-btn');
    const form = this;
    const notification = document.getElementById('notification');
    
    // Блокируем кнопку на время отправки
    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка...';
    
    // Собираем данные формы
    const formData = {
        user: document.getElementById('user_name').value.trim() || null,
        text: document.getElementById('review_text').value.trim()
    };
    
    try {
        // Отправляем запрос
        const response = await fetch('/reviews/add_review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Успешная отправка
            form.reset(); // Очищаем форму
            
            // Показываем уведомление
            notification.style.display = 'block';
            notification.classList.remove('fade-out');
            
            // Скрываем уведомление через 3 секунды
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.style.display = 'none';
                    notification.classList.remove('fade-out');
                }, 500);
            }, 3000);
            
            // Показываем дополнительное сообщение об успехе под формой (опционально)
            showTemporaryMessage('✓ Отзыв успешно отправлен!', 'success');
            
        } else {
            // Ошибка валидации
            let errorText = 'Ошибка при отправке: ';
            if (data.text) {
                errorText += data.text.join(' ');
            } else if (data.user) {
                errorText += data.user.join(' ');
            } else {
                errorText += 'Проверьте правильность заполнения формы';
            }
            
            showTemporaryMessage(errorText, 'error');
        }
    } catch (error) {
        // Ошибка сети или сервера
        console.error('Error:', error);
        showTemporaryMessage('Произошла ошибка при отправке. Попробуйте позже.', 'error');
    } finally {
        // Разблокируем кнопку
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить отзыв';
    }
});

// Функция для показа временных сообщений под формой
function showTemporaryMessage(message, type) {
    // Удаляем предыдущее сообщение, если оно есть
    const oldMessage = document.querySelector('.temporary-message');
    if (oldMessage) {
        oldMessage.remove();
    }
    
    // Создаем новое сообщение
    const messageDiv = document.createElement('div');
    messageDiv.className = `temporary-message ${type === 'success' ? 'success-message' : 'error-message'}`;
    messageDiv.textContent = message;
    
    // Добавляем после формы
    document.getElementById('reviews_form').after(messageDiv);
    
    // Удаляем через 5 секунд
    setTimeout(() => {
        if (messageDiv && messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// Добавляем обработчик для поля user - если поле пустое, отправляем null
document.getElementById('user_name').addEventListener('blur', function() {
    if (this.value.trim() === '') {
        this.value = ''; // Оставляем пустым
    }
});

// Валидация на клиенте (опционально)
document.getElementById('review_text').addEventListener('input', function() {
    if (this.value.trim().length < 5) {
        this.setCustomValidity('Отзыв должен содержать минимум 5 символов');
    } else {
        this.setCustomValidity('');
    }
});