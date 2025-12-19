// Функция для получения данных строки
function getRowData(row) {
    const cells = row.getElementsByTagName('td');
    const rowData = {};

    // Определяем, в каком tbody находится строка
    if (row.closest('#pinnedRows')) {
        rowData['ID'] = cells[0].querySelector('.unpin-button').getAttribute('data-id');
    } else {
        rowData['ID'] = cells[0].querySelector('.id_positoin_row').getAttribute('data-id');
    }

    rowData['Наименование'] = cells[5].innerText;
    rowData['Артикул'] = cells[3].innerText;
    rowData['Цвет'] = cells[10].querySelector('.circle_table').style.backgroundColor;
    rowData['Проект'] = cells[11].innerText;

    return rowData;
}

// Оптимизированная функция обновления данных
async function updateDetailsItem(data) {
    try {
        // 3. Делаем ОДИН запрос к серверу
        const response = await fetch(`get_details/article_id/${data.ID}/`);
        if (!response.ok) throw new Error('Ошибка сети');
        
        const additionalData = await response.json();

        
        // 1. Сначала обновляем данные, которые уже есть
        document.getElementById('position_name').textContent = data['Наименование'] || '';
        document.getElementById('position_article').textContent = data['Артикул'] || '';
        document.getElementById('project_name').textContent = data['Проект'] || '';
        
        // 2. Очищаем список проектов
        const projectsContainer = document.getElementById('item_project_popup');
        projectsContainer.innerHTML = '';
        
        
        // 4. Гарантированное обновление цвета
        const colorElement = document.getElementById('project_color');
        colorElement.style.backgroundColor = additionalData.status_one_project || 'transparent';
        
        // 5. Обновляем остальные данные
        document.getElementById('total_quantity').textContent = additionalData.total_quantity_by_project || '0';
        document.getElementById('unit').textContent = additionalData.base_unit || '';
        document.getElementById('count_projects').textContent = `(${additionalData.total_sum_any_projects || 0})`;
        document.getElementById('name_position').textContent = additionalData.title || '';
        document.getElementById('final_result_sum').textContent = additionalData.total_sum_any_projects || '0';
        document.getElementById('final_result_sum_unit').textContent = additionalData.base_unit || '';
        
        // 6. Быстрое обновление списка проектов
        additionalData.details_any_projects.forEach(project => {
            projectsContainer.insertAdjacentHTML('beforeend', `
                <div class="project_container">
                    <div class="project_status_popup">
                        <div class="circle" style="background-color: ${project.status_color || 'gray'}; width:10px;height:10px;border-radius:100%"></div>
                    </div>
                    <div class="project_name_popup">${project.project || ''}</div>
                    <div class="project_quantity_popup">${project.quantity || '0'}</div>
                    <div class="project_unit_popup">${project.base_unit || ''}</div>
                </div>
            `);
        });
        
    } catch (error) {
        console.error('Ошибка:', error);
        // Можно добавить отображение ошибки пользователю
    }
}

// Функция для добавления обработчика событий к tbody
function addRowClickListener(tbody) {
    tbody.addEventListener('click', function(event) {
        const target = event.target.closest('tr');
        if (target) {
            const data = getRowData(target);
            updateDetailsItem(data);
            detailsItem.style.display = 'block';
        }
    });
}

// Инициализация
const detailsItem = document.getElementById('details_item');
const hideInfoButton = document.getElementById('hide_info');

// Добавляем обработчики событий
addRowClickListener(document.getElementById('pinnedRows'));
addRowClickListener(document.getElementById('mainRows'));

// Обработчик скрытия информации
hideInfoButton.addEventListener('click', function(event) {
    detailsItem.style.display = 'none';
    event.stopPropagation();
});