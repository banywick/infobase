document.addEventListener('DOMContentLoaded', function() {
    // Константы для иконок (замените на свои пути)
    const ICON_EDIT = '/static/comers/icons/icon_edit.png';
    const ICON_STATUS = '/static/comers/icons/icon_status.png';
    const ICON_DELETE = '/static/comers/icons/icon_delete.png';
    
    // Ключ для localStorage
    const FILTER_STORAGE_KEY = 'invoice_filters';
    
    // Элементы DOM
    const supplierSelect = document.getElementById('id_supplier');
    const leadingSelect = document.getElementById('id_leading');
    const statusSelect = document.getElementById('id_status');
    const clearFilterBtn = document.getElementById('clear_filter');
    const tableBody = document.getElementById('invoiceTableBody');
    
    // Текущие данные таблицы
    let allData = [];
    let filteredData = [];
    
    // Стили для подсветки селектов
    const highlightStyle = {
        // backgroundColor: '#e8f5e9', // Светло-зеленый фон
        // borderColor: '#4caf50', // Зеленая рамка
        // color: '#2e7d32' // Темно-зеленый текст
    };
    
    const defaultStyle = {
        backgroundColor: '',
        borderColor: '',
        color: ''
    };
    
    // Применяем стили к селекту
    function applySelectStyles(selectElement, isHighlighted) {
        const styles = isHighlighted ? highlightStyle : defaultStyle;
        
        selectElement.style.backgroundColor = styles.backgroundColor;
        selectElement.style.borderColor = styles.borderColor;
        selectElement.style.color = styles.color;
        
        // Добавляем/удаляем класс для дополнительной стилизации через CSS
        if (isHighlighted) {
            selectElement.classList.add('filter-selected');
        } else {
            selectElement.classList.remove('filter-selected');
        }
    }
    
    // Обновляем стили всех селектов
    function updateSelectStyles() {
        applySelectStyles(supplierSelect, supplierSelect.value !== '');
        applySelectStyles(leadingSelect, leadingSelect.value !== '');
        applySelectStyles(statusSelect, statusSelect.value !== '');
    }
    
    // Загружаем сохраненные фильтры из localStorage
    function loadSavedFilters() {
        const savedFilters = localStorage.getItem(FILTER_STORAGE_KEY);
        if (savedFilters) {
            const filters = JSON.parse(savedFilters);
            
            if (filters.supplier) supplierSelect.value = filters.supplier;
            if (filters.leading) leadingSelect.value = filters.leading;
            if (filters.status) statusSelect.value = filters.status;
            
            // Обновляем стили после загрузки
            updateSelectStyles();
        }
    }
    
    // Сохраняем фильтры в localStorage
    function saveFilters() {
        const filters = {
            supplier: supplierSelect.value,
            leading: leadingSelect.value,
            status: statusSelect.value
        };
        localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
    }
    
    // Сбрасываем фильтры
    function clearFilters() {
        supplierSelect.value = '';
        leadingSelect.value = '';
        statusSelect.value = '';
        
        // Обновляем стили
        updateSelectStyles();
        
        // Удаляем из localStorage
        localStorage.removeItem(FILTER_STORAGE_KEY);
        
        // Показываем все данные
        filteredData = [...allData];
        renderTable(filteredData);
    }
    
    // Функция фильтрации данных
    function filterData() {
        const supplierValue = supplierSelect.value;
        const leadingValue = leadingSelect.value;
        const statusValue = statusSelect.value;
        
        // Обновляем стили селектов
        updateSelectStyles();
        
        // Сохраняем текущие фильтры
        saveFilters();
        
        // Фильтруем данные
        filteredData = allData.filter(item => {
            // Проверяем фильтр поставщика
            const supplierMatch = !supplierValue || 
                (item.supplier && item.supplier.id == supplierValue);
            
            // Проверяем фильтр ведущего
            const leadingMatch = !leadingValue || 
                (item.leading && item.leading.id == leadingValue);
            
            // Проверяем фильтр статуса
            const statusMatch = !statusValue || 
                (item.status && item.status.id == statusValue);
            
            // Все выбранные фильтры должны совпадать
            return supplierMatch && leadingMatch && statusMatch;
        });
        
        // Рендерим отфильтрованную таблицу
        renderTable(filteredData);
    }
    
    // Функция рендеринга таблицы
    function renderTable(data) {
        tableBody.innerHTML = '';
        
        if (data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="14" style="text-align: center; padding: 20px;">
                        Нет данных, соответствующих выбранным фильтрам
                    </td>
                </tr>
            `;
            return;
        }
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            // Извлекаем текстовые значения из вложенных объектов
            const commentText = item.comment ? item.comment.text : '';
            const leadingName = item.leading ? item.leading.name : '';
            const specialistName = item.specialist ? item.specialist.name : '';
            const statusName = item.status ? item.status.name : '';
            const supplierName = item.supplier ? item.supplier.name : '';
            
            row.innerHTML = `
                <td class="invoice-number">${item.invoice_number || ''}</td>
                <td class="date-cell">${item.date || ''}</td>
                <td class="supplier-cell">${supplierName}</td>
                <td class="article-cell">${item.article || ''}</td>
                <td>${item.name || ''}</td>
                <td>${item.unit || ''}</td>
                <td class="quantity-cell">${item.quantity || ''}</td>
                <td class="comment-cell">${commentText}</td>
                <td>${item.description_problem || ''}</td>
                <td>${specialistName}</td>
                <td>${leadingName}</td>
                <td class="status-cell">${statusName}</td>
                <td class="status-cell">${item.description || ''}</td>
                <td>
                    <div class="action_cell_table">
                        <div class="edit_invoice_button">
                            <img src="${ICON_EDIT}" alt="Редактировать">
                            <div class="open-btn" data-popup="popup5">Редактировать</div>
                        </div>
                        <div class="edit_invoice_button">
                            <img src="${ICON_STATUS}" alt="Статус">
                            <div class="open-btn" data-popup="popup6">Статус</div>
                        </div>
                        <div class="edit_invoice_button" data-id="${item.id}">
                            <img src="${ICON_DELETE}" alt="Удалить">
                            <div class="open-btn" data-popup="popup7">Удалить</div>
                        </div>
                    </div>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    // Загружаем данные с сервера
    function loadData() {
        fetch('/comers/get_all_positions/')
            .then(response => response.json())
            .then(data => {
                allData = data;
                filteredData = [...allData];
                
                // Загружаем сохраненные фильтры
                loadSavedFilters();
                
                // Применяем фильтры после загрузки данных
                filterData();
            })
            .catch(error => {
                console.error('Error fetching positions:', error);
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="14" style="text-align: center; color: red; padding: 20px;">
                            Ошибка загрузки данных
                        </td>
                    </tr>
                `;
            });
    }
    
    // Назначаем обработчики событий
    supplierSelect.addEventListener('change', filterData);
    leadingSelect.addEventListener('change', filterData);
    statusSelect.addEventListener('change', filterData);
    
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', clearFilters);
    }
    
    // Загружаем данные при загрузке страницы
    loadData();
});