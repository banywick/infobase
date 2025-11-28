//Получение всех данных при загрузке html страницы
document.addEventListener('DOMContentLoaded', function() {
    fetch('/comers/get_all_positions/')  // Замените на ваш URL
        .then(response => response.json())
        .then(data => {
            // Обработка данных и отображение их на странице
            console.log(data);
        })
        .catch(error => {
            console.error('Error fetching positions:', error);
        });

          // Второй fetch запрос с отображением фильтров
        fetch('/comers/get_filter_invoice_data/', {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            console.log('Фильтры из сесии пользователя:', data);
        })
        .catch(error => {
            console.error('Error in second fetch:', error);
        });
});

