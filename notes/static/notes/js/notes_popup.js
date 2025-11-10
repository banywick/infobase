document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы
    const addNotesBtn = document.getElementById('add_notes');
    const popup = document.querySelector('.popup_note');
    const closePopupBtn = document.querySelector('.close_popup');
    const overlay = document.querySelector('.background-overlay');

    // Функция открытия popup
    function openPopup() {
        popup.style.display = 'block';
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Блокируем скролл страницы
    }

    // Функция закрытия popup
    function closePopup() {
        popup.style.display = 'none';
        overlay.style.display = 'none';
        document.body.style.overflow = ''; // Разблокируем скролл страницы
    }

    // Открываем popup по клику на кнопку
    addNotesBtn.addEventListener('click', openPopup);

    // Закрываем popup по клику на крестик
    closePopupBtn.addEventListener('click', closePopup);

    // Закрываем popup по клику на фон
    overlay.addEventListener('click', closePopup);

    // Закрываем popup по нажатию Esc
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
        }
    });
});