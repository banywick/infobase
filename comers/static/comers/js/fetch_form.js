// document.getElementById('add_supler_form').addEventListener('submit', function(event) {
//     event.preventDefault(); // Предотвращаем стандартное поведение отправки формы
//     submitAddSupplerForm();
// });
// function submitAddSupplerForm() {
//     const formData = new FormData(document.getElementById('add_supler_form'));
//     const csrfToken = getCSRFToken();
//     fetch('/comers/add_supplier/', {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': csrfToken // Отправляем CSRF-токен в заголовке
//         },
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log(data);
//     })
//     .catch(error => {
//         console.error('Ошибка:', error);
//     });
// }

// function getCSRFToken() {
//     return getCookie('csrftoken'); // Используем функцию для получения CSRF-токена из куки
// }

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }