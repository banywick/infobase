    // Добавляем обработчик событий для кнопок
    tbody.addEventListener('click', function(event) {
        if (event.target.closest('#id_positoin_row')) {
            const button = event.target.closest('#id_positoin_row');
            console.log(button.getAttribute('data-id'));
        }
    });

    // URL, на который нужно отправить запрос
    const url = `http://127.0.0.1:8000/finder/add_fix_positions_to_session/${id}/`;

    // // Отправьте fetch запрос
    // fetch(url, {
    //     method: 'POST', // или 'GET', в зависимости от вашего API
    //     headers: {
    //         'Content-Type': 'application/json',
    //         // Добавьте другие заголовки, если необходимо
    //     },
    //     // Если нужно отправить данные в теле запроса, используйте body
    //     // body: JSON.stringify({ key: 'value' })
    // })
    // .then(response => response.json())
    // .then(data => {
    //     console.log('Success:', data);
    // })
    // .catch((error) => {
    //     console.error('Error:', error);
    // });
