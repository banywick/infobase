// Обработчики поиска
document.getElementById('search_icon').addEventListener('click', handleSearch);
document.getElementById('search_form').addEventListener('submit', handleSearch);

// Объединяем логику поиска в одну функцию
function handleSearch(event) {
    event.preventDefault();
    const searchData = getFormData();
    performSearch(searchData);
}

// Функция для получения данных формы
function getFormData() {
    const form = document.getElementById('search_form');
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    return data;
}

// Основная функция выполнения поиска
function performSearch(searchData) {
    const tbody = document.querySelector('tbody:not(.pinned-block)');
    const not_found = document.querySelector('.not_found');
    const infoWindow = document.querySelector('.info_window');
    
    // Показываем состояние загрузки
    tbody.innerHTML = '<tr><td colspan="12" class="loading">Загрузка данных...</td></tr>';
    not_found.style.display = 'none';
    infoWindow.style.display = 'none';
    infoWindow.innerHTML = '';

    fetch('/finder/products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(searchData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Results:', data.results);
        console.log('Analogs:', data.analogs);
        
      // В функции performSearch, в части обработки аналогов:
        if (data.analogs && data.analogs.length > 0) {
        infoWindow.style.display = 'flex'; // Изменено на flex
        infoWindow.style.flexDirection = 'column';

        const title = document.createElement('h3');
        title.textContent = 'Аналоги';
        title.className = 'analogs-title';

        const listContainer = document.createElement('div');
        listContainer.className = 'analogs-container';

        data.analogs.forEach(analog => {
            const analogItem = document.createElement('div');
            analogItem.className = 'analog-item';
            analogItem.textContent = analog;
            listContainer.appendChild(analogItem);
        });

        infoWindow.innerHTML = ''; // Очищаем перед добавлением
        infoWindow.appendChild(title);
        infoWindow.appendChild(listContainer);
        }
    

        
        // Обрабатываем основные результаты
        renderTableData(data.results, tbody, not_found);
    })
    .catch(error => {
        console.error('Error:', error);
        tbody.innerHTML = '<tr><td colspan="12" class="error">Ошибка загрузки данных</td></tr>';
    });
}

// Функция рендеринга данных таблицы
function renderTableData(data, tbody, not_found) {
    tbody.innerHTML = '';
    
    if(data.detail === "Ничего не найдено") {
        not_found.style.display = 'block';
        return;
    }
    
    not_found.style.display = 'none';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.classList.add('table-row');
        
        row.innerHTML = `
            <td class="icon-column">
                <button class="id_positoin_row" data-id="${item.id}">
                    <img id="keep_icon" src="${staticUrls.keepIcon}" alt="">
                </button>
            </td>
            <td class="icon-column">
                ${item.notes_part ? `
                    <div class="notes-icon-container">
                        <img src="${staticUrls.commentIcon}" alt="" class="notes-icon">
                        <div class="tooltip">${item.notes_part}</div>
                    </div>` : ''}
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
                <div class="circle_table"
                    style="background-color: ${item.status_color};
                    width:10px;
                    height:10px;
                    border-radius:100%">
                </div>
            </td>
            <td class="data-column">${item.project}</td>
            <td class="data-column">${item.comment || ''}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Обработчик для кнопок закрепления
    tbody.addEventListener('click', function(event) {
        if (event.target.closest('.id_positoin_row')) {
            const button = event.target.closest('.id_positoin_row');
            const data_id = button.getAttribute('data-id');
            
            fetch(`/finder/add_fix_positions_to_session/${data_id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                button.closest('tr')?.remove();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
}

// Функция для получения CSRF-токена
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