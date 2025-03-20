// Обработчик для клика по значку увеличительного стекла
document.getElementById('search_icon').addEventListener('click', function(event) {
    handleSearch(event);
});

// Обработчик для отправки формы (нажатие Enter)
document.getElementById('search_form').addEventListener('submit', function(event) {
    handleSearch(event);
});

function handleSearch(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение отправки формы

    const form = document.getElementById('search_form');
    const formData = new FormData(form);
    const data = {};

    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch('/finder/products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Очищаем таблицу перед добавлением новых данных
        const tbody = document.querySelector('tbody:not(.pinned-block)');
        var not_found = document.querySelector('.not_found')
        tbody.innerHTML = ''; // Очищаем содержимое tbody
        if(data.detail === "Ничего не найдено") {
            console.log('Ничего не найдено.')
            not_found.style.display = 'block'
        } else {
        not_found.style.display = 'none'   

        // Добавляем новые строки в таблицу
        data.forEach(item => {
            const row = document.createElement('tr');
            row.classList.add('table-row');

            // Иконка закрепления
            row.innerHTML = `
                <td class="icon-column">
                    <button class="id_positoin_row" data-id="${item.id}">
                        <img id="keep_icon" src="${staticUrls.keepIcon}" alt="">
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

            tbody.appendChild(row); // Добавляем строку в таблицу
        })};

        // Добавляем обработчик событий для кнопок
        tbody.addEventListener('click', function(event) {
            if (event.target.closest('.id_positoin_row')) {
                const button = event.target.closest('.id_positoin_row');
                const data_id = button.getAttribute('data-id');
                console.log(data_id);

                // Создаём URL внутри обработчика событий
                const url = `/finder/add_fix_positions_to_session/${data_id}/`;

                // Отправляем fetch запрос
                fetch(url, {
                    method: 'POST', // или 'GET', в зависимости от вашего API
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
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
    .catch(error => console.error('Error:', error));
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
