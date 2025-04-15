// Отправка названия проекта который выбрал пользователь
let selectedProject = null;

// Обработчик клика на элементы проектов
document.addEventListener('click', function(e) {
    const projectContent = e.target.closest('.project-content');
    if (projectContent) {
        const projectSpan = projectContent.querySelector('span');
        if (projectSpan) {
            selectedProject = projectSpan.textContent.trim();
            console.log('Выбран проект:', selectedProject); // Для отладки
            
            // Визуальное выделение
            document.querySelectorAll('.project-content').forEach(el => {
                el.classList.remove('selected');
            });
            projectContent.classList.add('selected');
        }
    }
});

// Обработчик клика на кнопку фильтра
document.getElementById('button_filter_view_all').addEventListener('click', async function() {
    const popup = document.getElementById('choice_project_popup');
    const tbody = document.querySelector('tbody:not(.pinned-block)');
    const not_found = document.querySelector('.not_found');
    
    if (!selectedProject) {
        alert('Пожалуйста, выберите проект');
        return;
    }
    
    try {
        console.log('Отправляемые данные:', { project: selectedProject }); // Для отладки
        
        // Показываем состояние загрузки
        tbody.innerHTML = '<tr><td colspan="12" class="loading">Загрузка данных...</td></tr>';
        not_found.style.display = 'none';

        const response = await fetch('/finder/all_products_filter_project/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ project_name: selectedProject })
        });
        
        if (!response.ok) throw new Error('Ошибка сервера');
        
        const data = await response.json();
        console.log('Ответ сервера:', data);
        
        
        // Рендерим полученные данные
        renderTableData(data, tbody, not_found);
        
        // Закрываем popup только после успешного выполнения
        if (popup) popup.style.display = 'none';
        
    } catch (error) {
        console.error('Ошибка:', error);
        tbody.innerHTML = '<tr><td colspan="12" class="error">Ошибка загрузки данных</td></tr>';
        alert('Произошла ошибка при отправке данных');
    }
});

selectedProject = null;

// Функция рендеринга данных таблицы (такая же как в основном JS)
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

// Функция для получения CSRF токена
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) return cookieValue;
    }
    return null;
}