document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('.filter_button');
    const form = document.getElementById('add_filter_form');

    button.addEventListener('click', function() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);

        // Первый fetch запрос
        fetch('/comers/add_filter_invoice_data/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response from first fetch:', data);
        })
        .catch(error => {
            console.error('Error in first fetch:', error);
        });

      
    });
});
