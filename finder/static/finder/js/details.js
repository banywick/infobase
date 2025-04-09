        // Функция для получения данных строки
        function getRowData(row) {
            const cells = row.getElementsByTagName('td');
            const rowData = {};


            // Определяем, в каком tbody находится строка
            if (row.closest('#pinnedRows')) {
            rowData['ID'] = cells[0].querySelector('.id_positoin_row_pin').getAttribute('data-id');
        } else {
            rowData['ID'] = cells[0].querySelector('.id_positoin_row').getAttribute('data-id');
        }

            rowData['Наименование'] = cells[5].innerText;
            rowData['Артикул'] = cells[3].innerText;
            rowData['Цвет'] = cells[10].querySelector('.circle_table').style.backgroundColor;
            rowData['Проект'] = cells[11].innerText;
            return rowData;
        }

             // Функция для обновления информации в details_item
            async function updateDetailsItem(data) {
                try {
                    // Выполняем fetch запрос
                    const response = await fetch(`get_details/article_id/${data.ID}/`);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const additionalData = await response.json();
                    console.log(additionalData)
            
                    // Обновляем элементы на странице
                    document.getElementById('position_name').innerText = data['Наименование'];
                    document.getElementById('position_article').innerText = data['Артикул'];
                    document.getElementById('project_color').style.backgroundColor = data['Цвет'];
                    document.getElementById('project_name').innerText = data['Проект'];
                    document.getElementById('total_quantity').innerText = additionalData.total_quantity_by_project;
                    document.getElementById('unit').innerText = additionalData.base_unit;
                    document.getElementById('count_projects').innerText = `(${additionalData.total_sum_any_projects})`;
                    document.getElementById('name_position').innerText = additionalData.title;
                    document.getElementById('final_result_sum').innerText = additionalData.total_sum_any_projects;
                    document.getElementById('final_result_sum_unit').innerText = additionalData.base_unit;
            
                // Получаем контейнер, в который будем добавлять новые элементы
                const container = document.getElementById('item_project_popup');

                // Очищаем контейнер перед добавлением новых элементов
                container.innerHTML = '';

                // Парсим список словарей и создаем элементы
                additionalData.details_any_projects.forEach(project => {
                    // Создаем контейнер для каждого проекта
                    const projectContainer = document.createElement('div');
                    projectContainer.className = 'project_container';
                    

                    // Создаем цветной кружок статуса (как в вашем примере)
                    const statusCircle = document.createElement('div');
                    statusCircle.className = 'circle';
                    statusCircle.style.backgroundColor = project.status_color;
                    statusCircle.style.width = '10px';
                    statusCircle.style.height = '10px';
                    statusCircle.style.borderRadius = '100%';
                
                    // Создаем контейнер для статуса (если нужно подпись рядом с кружком)
                    const projectStatusDiv = document.createElement('div');
                    projectStatusDiv.className = 'project_status_popup';
                    projectStatusDiv.appendChild(statusCircle);
                    // projectStatusDiv.appendChild(document.createTextNode(' ' + project.status)); // если нужно текст статуса
                
                    // Остальные элементы
                    const projectNameDiv = document.createElement('div');
                    projectNameDiv.className = 'project_name_popup';
                    projectNameDiv.innerText = project.project;
                
                    const projectQuantityDiv = document.createElement('div');
                    projectQuantityDiv.className = 'project_quantity_popup';
                    projectQuantityDiv.innerText = project.quantity;
                
                    const projectUnitDiv = document.createElement('div');
                    projectUnitDiv.className = 'project_unit_popup';
                    projectUnitDiv.innerText = project.base_unit;
                
                    // Собираем структуру
                    projectContainer.appendChild(projectStatusDiv); // Добавляем кружок первым
                    projectContainer.appendChild(projectNameDiv);
                    projectContainer.appendChild(projectQuantityDiv);
                    projectContainer.appendChild(projectUnitDiv);
                
                    container.appendChild(projectContainer);
                });
            
                } catch (error) {
                    console.error('Fetch error:', error);
                }
            }

        // Функция для добавления обработчика событий к tbody
        function addRowClickListener(tbody) {
            tbody.addEventListener('click', function(event) {
                const target = event.target.closest('tr');
                if (target) {
                    const data = getRowData(target);
                    console.log(data.ID);
                    updateDetailsItem(data);
                    detailsItem.style.display = 'block'; // Показываем details_item при клике на строку
                }
            });
            addEventListener('click', function(event) {
                detailsItem.style.display = 'block';

            })


        }

        // Добавляем обработчики событий к обоим tbody
        addRowClickListener(document.getElementById('pinnedRows'));
        addRowClickListener(document.getElementById('mainRows'));
        const detailsItem = document.getElementById('details_item');
        const hideInfoButton = document.getElementById('hide_info');

         // Обработчик события для кнопки "Скрыть информацию"
        hideInfoButton.addEventListener('click', function(event) {
            event.stopPropagation(); // Предотвращаем всплытие события
            detailsItem.style.display = 'none'; // Скрываем details_item
        });