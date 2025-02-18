document.addEventListener('DOMContentLoaded', function() {
    // Извлечение значения из атрибута данных
    const sidebar = document.querySelector('.sidebar');

    // Или извлечение значения из текста элемента
    const userGroupElement = document.getElementById('user-group');
    const userGroup = userGroupElement.textContent.trim();

    const links = document.querySelectorAll('.sidebar a');

     // Список разрешенных идентификаторов ссылок для группы "commers"
    const allowedLinkIdsForCommers = ['1', '2', '5', '7', '9'];
     // Список разрешенных идентификаторов ссылок для группы "commers"
    const allowedLinkIdsForSklad = ['1', '2', '3', '4', '5', '8', '9'];
     // Список разрешенных идентификаторов ссылок для тех кто не состоит в группах"
    const allowedLinkIdsForAnanimus = ['1', '7', '9'];

    links.forEach(link => {
        const linkId = link.getAttribute('data-link-id');

        if (userGroup === 'commers') {
            // группа коммерсанты
            if (!allowedLinkIdsForCommers.includes(linkId)) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } else if (!userGroup || userGroup === 'None' || userGroup === 'undefined') {
            // Анонимные пользователи
            if (!allowedLinkIdsForAnanimus.includes(linkId)) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } else if (userGroup === 'sklad') {
            // группа склад
            if (!allowedLinkIdsForSklad.includes(linkId)) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } 
    });
});