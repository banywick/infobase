document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('.send_data_form_button');
    const form = document.getElementById('inputDataForm');

    button.addEventListener('click', function() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);


        fetch('/comers/add_invoice_data/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
    })});