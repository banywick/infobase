document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar');
    const userGroup = sidebar.getAttribute('data-user-group');
    const links = document.querySelectorAll('.sidebar a');

    links.forEach(link => {
        if (userGroup === 'commers') {
            // Доступна только ссылка "Комерсанты"
            if (link.getAttribute('data-link-id') !== '3') {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } else if (userGroup === 'коммерсанты') {
            // Доступны только первые три ссылки
            if (link.getAttribute('data-link-id') > 4) {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        } else {
            // Анонимные пользователи, доступна только одна ссылка
            if (link.getAttribute('data-link-id') !== '1') {
                link.style.pointerEvents = 'none';
                link.style.color = 'gray'; // Пример стиля для неактивных ссылок
            }
        }
    });
});