document.addEventListener('DOMContentLoaded', function() {
    const titleCount = document.querySelector('.title_count');
    const button_update = document.querySelector('.button_wrapper_update');
    const backgroundOverlay = document.querySelector('.background-overlay');
    const popup = document.querySelector('.any_projects_popup');
    const upload_popup = document.querySelector('.upload_popup');
    const closeIcon = document.querySelector('.close');
    const closeUpdate = document.getElementById('close_update');
    const closeButton = document.querySelector('.button_wrapper_close');

    titleCount.addEventListener('click', function() {
        backgroundOverlay.style.display = 'block';
        popup.style.display = 'block';
    });
    button_update.addEventListener('click', function() {
        backgroundOverlay.style.display = 'block';
        upload_popup.style.display = 'block';
    });

    closeIcon.addEventListener('click', function() {
        backgroundOverlay.style.display = 'none';
        popup.style.display = 'none';
    });

    closeUpdate.addEventListener('click', function() {
        backgroundOverlay.style.display = 'none';
        upload_popup.style.display = 'none';
    });

    closeButton.addEventListener('click', function() {
        backgroundOverlay.style.display = 'none';
        popup.style.display = 'none';
    });
});
