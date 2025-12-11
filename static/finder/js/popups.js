document.addEventListener('DOMContentLoaded', function() {
    // Элементы попапов
    const backgroundOverlay = document.querySelector('.background-overlay');
    const anyProjectsPopup = document.querySelector('.any_projects_popup');
    const uploadPopup = document.querySelector('.upload_popup');
    const choiceProjectPopup = document.querySelector('.choice_project_popup');
    const all_positions_button = document.getElementById('button_filter_view_all');
    const filter_submit = document.getElementById('button_filter_submit');
    
    // Кнопки открытия
    const titleCount = document.querySelector('.title_count');
    const buttonUpdate = document.querySelector('.button_wrapper_update');
    const filterButton = document.getElementById('button_filter_projects');
    
    // Кнопки закрытия
    const closeIcons = document.querySelectorAll('.close');
    const closeUpdate = document.getElementById('close_update');
    const closeButtons = document.querySelectorAll('.button--red');

    // Общие функции для управления попапами
    function openPopup(popupElement) {
        backgroundOverlay.style.display = 'block';
        popupElement.style.display = 'block';
        
        // Специальная логика для choice_project_popup
        if (popupElement === choiceProjectPopup && typeof window.loadProjectsIntoPopup === 'function') {
            window.loadProjectsIntoPopup();
        }
    }




    function closeAllPopups() {
        backgroundOverlay.style.display = 'none';
        anyProjectsPopup.style.display = 'none';
        uploadPopup.style.display = 'none';
        choiceProjectPopup.style.display = 'none';
    }

    // Обработчики открытия
    if (titleCount) {
        titleCount.addEventListener('click', () => openPopup(anyProjectsPopup));
    }
    
    if (buttonUpdate) {
        buttonUpdate.addEventListener('click', () => openPopup(uploadPopup));
    }
    
    if (filterButton) {
        filterButton.addEventListener('click', () => openPopup(choiceProjectPopup));
    }

       // Добавляем обработчики для кнопок all_positions_button и filter_submit
    if (all_positions_button) {
        all_positions_button.addEventListener('click', closeAllPopups);
    }
    
    if (filter_submit) {
        filter_submit.addEventListener('click', closeAllPopups);
    }

    // Обработчики закрытия
    closeIcons.forEach(icon => {
        icon.addEventListener('click', closeAllPopups);
    });
    
    if (closeUpdate) {
        closeUpdate.addEventListener('click', closeAllPopups);
    }
    
    closeButtons.forEach(button => {
        button.addEventListener('click', closeAllPopups);
    });

    // Закрытие при клике на оверлей
    if (backgroundOverlay) {
        backgroundOverlay.addEventListener('click', closeAllPopups);
    }

    // Закрытие при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllPopups();
        }
    });
});