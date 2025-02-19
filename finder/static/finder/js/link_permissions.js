document.addEventListener('DOMContentLoaded', function() {
    // Получаем разрешенные имена ссылок для аутентифицированных пользователей
    const allowedLinkNames = JSON.parse(document.getElementById('allowed-link-names').textContent);
    const links = document.querySelectorAll('.sidebar a');
    const userGroupElement = document.getElementById('user-group');
    const userGroup = userGroupElement.textContent.trim();

    // Список разрешенных ссылок для анонимных пользователей
    const allowedLinkIdsForAnonymous = ['поиск', 'заметки', 'Отзывы и предложения'];

    links.forEach(link => {
        const linkName = link.getAttribute('data-link-name');

        if (userGroup === 'None') {
            // Логика для анонимных пользователей
            if (!allowedLinkIdsForAnonymous.includes(linkName)) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } else {
            // Логика для аутентифицированных пользователей
            if (!allowedLinkNames.includes(linkName)) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        }
    });
});