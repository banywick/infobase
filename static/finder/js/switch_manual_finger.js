// Элементы
const menuRowFind = document.getElementById('menu_row_find');
const manualElement = document.querySelector('.manual');
const searchInput = document.getElementById('search_input');
const buttonViewAll = document.getElementById('button_filter_view_all');
const buttonSubmit = document.getElementById('button_filter_submit');

// 1. Переключение manual при клике на menu_row_find
menuRowFind.addEventListener('click', function() {
    if (manualElement.style.display === 'none' || manualElement.style.display === '') {
        manualElement.style.display = 'block';
    } else {
        manualElement.style.display = 'none';
    }
});

// 2. Скрыть manual при вводе в search_input
searchInput.addEventListener('input', function() {
    manualElement.style.display = 'none';
});

// 3. Скрыть manual при клике на кнопки
buttonViewAll?.addEventListener('click', function() {
    manualElement.style.display = 'none';
});

buttonSubmit?.addEventListener('click', function() {
    manualElement.style.display = 'none';
});