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
            function updateDetailsItem(data) {
                document.getElementById('position_name').innerText = data['Наименование'];
                document.getElementById('position_article').innerText = data['Артикул'];
                document.getElementById('project_color').style.backgroundColor = data['Цвет'];
                document.getElementById('project_name').innerText = data['Проект'];
            }

        // Функция для добавления обработчика событий к tbody
        function addRowClickListener(tbody) {
            tbody.addEventListener('click', function(event) {
                const target = event.target.closest('tr');
                if (target) {
                    const data = getRowData(target);
                    console.log(data);
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