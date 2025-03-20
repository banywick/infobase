document.addEventListener('DOMContentLoaded', function() {
    // Выполняем fetch запрос при загрузке страницы
    fetchData();

    // Добавляем обработчик клика на элемент с классом id_positoin_row
    document.addEventListener('click', function(event) {
        if (event.target.closest('.id_positoin_row')) {
            const button = event.target.closest('.id_positoin_row');
            console.log(button, 'кнопка таблицы');

            // Устанавливаем задержку в 1 секунду перед выполнением fetch запроса
            setTimeout(function() {
                fetchData();
            }, 1000); // 1000 миллисекунд = 1 секунда
        }
    });
});

function fetchData() {
    fetch('/finder/get_fixed_positions/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => response.json())
    .then(data => {
        // Данные из сессии с закрепленными позициями
        // console.log('Success:', data);

        // Преобразуем объект в массив значений
        const dataArray = Object.values(data);
        console.log(dataArray);

        // Найдите элемент, в который нужно добавить строки
        const pinnedRows = document.getElementById('pinnedRows');

        // Очищаем текущие строки перед добавлением новых
        pinnedRows.innerHTML = '';

        // Добавляем новые строки в блок закрепленных позиций
        dataArray.forEach(item => {
            const row = document.createElement('tr'); // Используем document.createElement
            row.classList.add('table-row');

            // Иконка закрепления
            row.innerHTML = `
                <td class="icon-column">
                    <button class="id_positoin_row_pin" data-id="${item.id}">
                        <img id="keep_icon_pin" src="${staticUrls.keepIconRed}" alt="">
                    </button>
                </td>
                <td class="icon-column">
                    ${item.notes_part ? `
                        <div class="notes-icon-container">
                            <img src="${staticUrls.commentIcon}" alt="" class="notes-icon">
                            <div class="tooltip">${item.notes_part}</div></div> ` : ''}
                </td>
                <td class="data-column">${item.party}</td>
                <td class="data-column">${item.article}</td>
                <td class="data-column">${item.code}</td>
                <td class="data-column">${item.title}</td>
                <td class="icon-column">
                    <img src="${staticUrls.copyIcon}" alt="">
                </td>
                <td class="data-column">${item.quantity}</td>
                <td class="data-column">${item.base_unit}</td>
                <td class="data-column">${item.price}</td>
                <td class="icon-column">
                    <div class="circle_table" style="background-color: ${item.status_color};"></div>
                </td>
                <td class="data-column">${item.project}</td>
                <td class="data-column">${item.comment || ''}</td> <!-- Если комментарий null, выводим пустую строку -->
            `;

            pinnedRows.appendChild(row); // Добавляем строку в таблицу
        });

        pinnedRows.addEventListener('click', function(event) {
            if (event.target.closest('.id_positoin_row_pin')) {
                const button = event.target.closest('.id_positoin_row_pin');
                const data_id = button.getAttribute('data-id');
                console.log(data_id);

                // Создаём URL внутри обработчика событий
                const url = `/finder/remove_fix_positions_to_session/${data_id}/`;

                // Отправляем fetch запрос
                fetch(url, {
                    method: 'POST', // или 'GET', в зависимости от вашего API
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    // Если нужно отправить данные в теле запроса, используйте body
                    // body: JSON.stringify({ key: 'value' })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);

                    // Удаление всей строки из таблицы
                    const rowToRemove = button.closest('tr');
                    if (rowToRemove) {
                        rowToRemove.remove();
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Функция для получения CSRF-токена
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
