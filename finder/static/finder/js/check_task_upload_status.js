const submit_button = document.querySelector('.button');
submit_button.addEventListener('click', (event) => {
    // Проверяем, был ли клик реальным (не автоматическим)
    if (event.isTrusted) {
        checkTaskStatus();
    }
});

function checkTaskStatus() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('doc', fileInput.files[0]);

    fetch('/finder/upload/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Обработайте полученные данные
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
