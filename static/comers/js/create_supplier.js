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
            if (!response.ok) {
                return response.json().then(err => {
                    throw err;
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Перезагружаем страницу при успешном добавлении
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            // Отображаем ошибки под полями
            displayErrors(error);
        });
    });
});
