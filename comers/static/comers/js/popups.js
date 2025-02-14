function openPopup(popupId) {
    document.querySelector(`.${popupId}`).style.display = 'block';
    document.querySelector('.overlay').style.display = 'block';
}

function closePopup() {
    document.querySelector('.menu_filter').style.display = 'none';
    document.querySelector('.add_suppler').style.display = 'none';
    document.querySelector('.input_data_form').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
}