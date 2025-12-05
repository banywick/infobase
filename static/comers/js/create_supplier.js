document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add_suppler_form');

    // Функция для отображения ошибок под полями
    function displayErrors(errors) {
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

    // Обработчик отправки формы (и для кнопки, и для Enter)
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Отменяем стандартное поведение формы

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
                window.location.reload();
            } else {
                return response.json().then(errors => {
                    throw errors;
                });
            }
        })
        .catch(errors => {
            console.error('Ошибки:', errors);
            if (errors && typeof errors === 'object') {
                displayErrors(errors);
            } else {
                alert('Произошла неизвестная ошибка. Проверьте консоль.');
            }
        });
    });
});
