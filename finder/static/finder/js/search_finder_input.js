document.getElementById('search_icon').addEventListener('click', function(event) {
    event.preventDefault();
    const form = document.getElementById('search_form');
    const formData = new FormData(form);
    const data = {};

    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch('/finder/products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Очищаем таблицу перед добавлением новых данных
        const tbody = document.querySelector('tbody:not(.pinned-block)');
        tbody.innerHTML = ''; // Очищаем содержимое tbody

        // Добавляем новые строки в таблицу
        data.forEach(item => {
            const row = document.createElement('tr');
            row.classList.add('table-row');

            // Иконка закрепления
            row.innerHTML = `
                <td class="icon-column">
                    <button onclick="pinRow(this)">
                        <img src="${staticUrls.keepIcon}" alt="">  
                    </button>
                </td>
                <td class="icon-column">
                    <img src="${staticUrls.commentIcon}" alt="">    
                </td>
                <td class="data-column">${item.party}</td>
                <td class="data-column">${item.article}</td>
                <td class="data-column">${item.code}</td>
                <td class="data-column">${item.title}</td>
                <td class="icon-column">
                    <img src="${staticUrls.copyIcon}" alt=""> 
                </td>
                <td class="data-column">${item.quantity}</td>
                <td class="data-column">${item.base_unit}</td>
                <td class="data-column">${item.price}</td>
                <td class="icon-column">
                    <div class="circle_table" style="background-color: ${item.status_color};"></div>
                </td>
                <td class="data-column">${item.project}</td>
                <td class="data-column">${item.comment || ''}</td> <!-- Если комментарий null, выводим пустую строку -->
            `;

            tbody.appendChild(row); // Добавляем строку в таблицу
        });
    })
    .catch(error => console.error('Error:', error));
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}