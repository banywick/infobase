document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('.send_data_form_button');
    const form = document.getElementById('inputDataForm');

    button.addEventListener('click', function() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);

        // Выводим данные в консоль для предварительного просмотра
        console.log(formData);

        fetch('/comers/add_invoice_data/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Перезагружаем страницу или выполняем другие действия
                location.reload('/shortfalls');
            } else {
                // Ошибка валидации, отобразить ошибки в форме
                for (const field in data.errors) {
                    const errorElement = document.createElement('div');
                    errorElement.classList.add('error');
                    errorElement.textContent = data.errors[field][0];
                    document.querySelector(`#id_${field}`).parentNode.appendChild(errorElement);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});