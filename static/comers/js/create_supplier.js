document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.querySelector('.button_supplier');
    const form = document.getElementById('add_suppler_form');

    // Функция для отображения ошибок под полями
    function displayErrors(errors) {
        // Удаляем предыдущие ошибки
        const existingErrors = form.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());

        // Отображаем новые ошибки
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

    submitButton.addEventListener('click', function() {
        const formData = new FormData(form);

        fetch('/comers/add_supplier/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => {
            if (response.ok) {
                // Если ответ успешный (201 Created или 200 OK без ошибок)
                window.location.reload(); // Перезагружаем страницу
            } else {
                // Если ответ с ошибками (400 Bad Request)
                return response.json().then(errors => {
                    throw errors; // Передаём ошибки в catch
                });
            }
        })
        .catch(errors => {
            console.error('Ошибки:', errors);
            // Отображаем ошибки под полями
            if (errors && typeof errors === 'object') {
                displayErrors(errors);
            } else {
                alert('Произошла неизвестная ошибка. Проверьте консоль.');
            }
        });
    });
});
