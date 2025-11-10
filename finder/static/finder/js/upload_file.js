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
        const not_file_info = document.querySelector('.not_file_info');
        not_file_info.innerHTML = '';

        if (uploadData.task_id) {
            checkTaskStatus(uploadData.task_id);
        }
        if (uploadData.doc && uploadData.doc[0]) {
            console.log('Данные существуют')
            // load_errors.innerHTML = uploadData.doc[0];
            not_file_info.innerHTML = 'Не выбран файл!';
        }

        
    })
    .catch(error => console.error('Error:', error));
}


document.addEventListener('DOMContentLoaded', function() {
    // Обработка отображения имени файла
    const fileInput = document.getElementById('fileInput');
    const fileNameSpan = document.querySelector('.file-name');
    
    if (fileInput && fileNameSpan) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileNameSpan.textContent = this.files[0].name;
                fileNameSpan.style.color = '#4b5563';
            } else {
                fileNameSpan.textContent = 'Файл не выбран';
                fileNameSpan.style.color = '#6b7280';
            }
        });
    }
    
    // Функции для показа/скрытия popup
    window.showPopup = function() {
        const popup = document.querySelector('.upload_popup');
        if (popup) {
            popup.style.display = 'block';
            setTimeout(() => {
                popup.classList.add('active');
            }, 10);
        }
    };
    
});







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
