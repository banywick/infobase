document.addEventListener('DOMContentLoaded', function() {
    const titleCount = document.querySelector('.title_count');
    const backgroundOverlay = document.querySelector('.background-overlay');
    const popup = document.querySelector('.any_projects_popup');
    const closeIcon = document.querySelector('.close');
    const closeButton = document.querySelector('.button_wrapper_close');

    titleCount.addEventListener('click', function() {
        backgroundOverlay.style.display = 'block';
        popup.style.display = 'block';
    });

    closeIcon.addEventListener('click', function() {
        backgroundOverlay.style.display = 'none';
        popup.style.display = 'none';
    });

    closeButton.addEventListener('click', function() {
        backgroundOverlay.style.display = 'none';
        popup.style.display = 'none';
    });
});
