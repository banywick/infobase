// static/comers/js/filters.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    // Элементы фильтров
    const supplierSelect = document.getElementById('id_supplier');
    const leadingSelect = document.getElementById('id_leading');
    const statusSelect = document.getElementById('id_status');
    const clearFilterBtn = document.getElementById('clear_filter');
    
    if (!supplierSelect || !leadingSelect || !statusSelect) return;
    
    // Загружаем сохраненные фильтры
    function loadSavedFilters() {
        const savedFilters = ComersApp.loadFilters();
        if (savedFilters) {
            if (savedFilters.supplier) supplierSelect.value = savedFilters.supplier;
            if (savedFilters.leading) leadingSelect.value = savedFilters.leading;
            if (savedFilters.status) statusSelect.value = savedFilters.status;
            applyFilters();
        }
    }
    
    // Применяем фильтры
    function applyFilters() {
        const filters = {
            supplier: supplierSelect.value,
            leading: leadingSelect.value,
            status: statusSelect.value
        };
        
        // Сохраняем фильтры
        ComersApp.saveFilters(filters);
        
        // Фильтруем данные
        const allData = ComersApp.getAllData();
        const filteredData = allData.filter(item => {
            const supplierMatch = !filters.supplier || 
                (item.supplier && item.supplier.id == filters.supplier);
            
            const leadingMatch = !filters.leading || 
                (item.leading && item.leading.id == filters.leading);
            
            const statusMatch = !filters.status || 
                (item.status && item.status.id == filters.status);
            
            return supplierMatch && leadingMatch && statusMatch;
        });
        
        // Устанавливаем отфильтрованные данные
        ComersApp.setFilteredData(filteredData);
        
        // Перерисовываем таблицу
        ComersApp.renderTable();
        
        // Обновляем стили селектов
        updateSelectStyles();
    }
    
    function updateSelectStyles() {
        [supplierSelect, leadingSelect, statusSelect].forEach(select => {
            if (select.value) {
                select.classList.add('filter-selected');
            } else {
                select.classList.remove('filter-selected');
            }
        });
    }
    
    // Обработчики событий
    supplierSelect.addEventListener('change', applyFilters);
    leadingSelect.addEventListener('change', applyFilters);
    statusSelect.addEventListener('change', applyFilters);
    
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            supplierSelect.value = '';
            leadingSelect.value = '';
            statusSelect.value = '';
            
            ComersApp.clearFilters();
            ComersApp.setFilteredData([...ComersApp.getAllData()]);
            ComersApp.renderTable();
            updateSelectStyles();
        });
    }
    
    // Инициализация
    loadSavedFilters();
});