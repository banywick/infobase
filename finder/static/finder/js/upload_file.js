const submit_button = document.querySelector('.button');
submit_button.addEventListener('click', (event) => {
    // Проверяем, был ли клик реальным (не автоматическим)
    if (event.isTrusted) {
        uploadDocumentAndCheckCelery();
    }
});

function uploadDocumentAndCheckCelery() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('doc', fileInput.files[0]);

    // Выполняем оба запроса параллельно
    Promise.all([
        fetch('/finder/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        }).then(response => response.json()),

        fetch("/finder/celery_status/").then(response => response.json())
    ])
    .then(([uploadData, celeryData]) => {
        console.log('Upload Data:', uploadData);
        console.log('Celery Status:', celeryData);

        if (uploadData.task_id) {
            checkTaskStatus(uploadData.task_id);
        }
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
