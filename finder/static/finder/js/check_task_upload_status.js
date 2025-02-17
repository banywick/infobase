
const load_animation = document.querySelector('.load_animation');
const load_errors = document.querySelector('.load_error');
const update_success = document.querySelector('.update_success');

function checkTaskStatus(taskId) {
    const intervalId = setInterval(() => {
        fetch(`/finder/get_task_upload_status/?task_id=${taskId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Обработайте полученные данные
            if (data.status === 'PENDING') {
                console.log('Обработка данных!');
                load_errors.innerHTML = ''
                load_animation.style.display = 'flex'

            }

            if (data.status === 'SUCCESS') {
                clearInterval(intervalId); // Останавливаем интервал, если задача завершена
                console.log('Task completed');
                update_success.innerHTML = data.result;
            
                // Задержка в 5 секунд перед перенаправлением
                setTimeout(() => {
                    window.location.href = "/finder/";
                }, 5000); // 5000 миллисекунд = 5 секунд
            }

            if (data.status === 'FAILURE') {
                clearInterval(intervalId); // Останавливаем интервал, если задача завершена
                load_animation.style.display = 'flex'
                load_errors.innerHTML = data.result
            }
        })
        .catch(error => console.error('Error:', error));
    }, 2000); // Запрос каждые 2 секунды
}

