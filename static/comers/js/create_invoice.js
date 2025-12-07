document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('inputDataForm');

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

    // Обработчик отправки формы (и для кнопки, и для Enter)
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Отменяем стандартное поведение формы

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);

        // Отладочный вывод: проверяем, что собирается в formData
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }

        fetch('/comers/add_invoice_data/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errors => {
                    throw errors; // Передаем ошибки в catch
                });
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.success) {
                // window.location.reload(); // Перезагружаем страницу при успехе
            }
        })
        .catch(errors => {
            console.error('Ошибки:', errors);
            if (errors && typeof errors === 'object') {
                displayErrors(errors); // Отображаем ошибки под полями
            } else {
                alert('Произошла неизвестная ошибка. Проверьте консоль.');
            }
        });
    });
});
