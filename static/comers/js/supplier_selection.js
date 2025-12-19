// Создайте новый файл static/comers/js/supplier_selection.js
document.addEventListener('DOMContentLoaded', function() {
    const supplierSearch = document.getElementById('supplier-search-datalist');
    const supplierHidden = document.getElementById('id_supplier_hidden');
    const supplierOptions = document.getElementById('supplier-options');
    const clearSearchBtn = document.getElementById('clear-search');
    const toggleListBtn = document.getElementById('toggle-list');
    const customDropdown = document.getElementById('custom-dropdown');
    const dropdownSearch = document.getElementById('dropdown-search');
    const dropdownOptions = document.getElementById('dropdown-options');
    const selectedSupplierId = document.getElementById('selected-supplier-id');
    const supplierValidation = document.getElementById('supplier-validation');

    if (!supplierSearch || !supplierHidden) return;

    // Загружаем все поставщики в массив
    const allSuppliers = Array.from(supplierOptions.options).map(option => ({
        id: option.dataset.id,
        name: option.value,
        element: option
    }));

    // Функция для обновления скрытого поля и отображения ID
    function updateSupplierField(supplierId, supplierName) {
        if (supplierId) {
            supplierHidden.value = supplierId;
            selectedSupplierId.textContent = `ID: ${supplierId}`;
            selectedSupplierId.style.display = 'inline-block';
            supplierValidation.style.display = 'inline-flex';
            console.log(`Выбран поставщик: ${supplierName} (ID: ${supplierId})`);
        } else {
            supplierHidden.value = '';
            selectedSupplierId.style.display = 'none';
            supplierValidation.style.display = 'none';
        }
    }

    // Функция для поиска поставщика по имени
    function findSupplierByName(name) {
        return allSuppliers.find(supplier => 
            supplier.name.toLowerCase() === name.toLowerCase()
        );
    }

    // Обработчик изменения поля поиска
    supplierSearch.addEventListener('input', function() {
        const searchValue = this.value.trim();
        
        if (searchValue === '') {
            updateSupplierField('', '');
            return;
        }

        // Ищем точное совпадение
        const foundSupplier = findSupplierByName(searchValue);
        
        if (foundSupplier) {
            updateSupplierField(foundSupplier.id, foundSupplier.name);
        } else {
            updateSupplierField('', '');
        }
    });

    // Обработчик выбора из datalist
    supplierSearch.addEventListener('change', function() {
        const selectedValue = this.value;
        const foundSupplier = findSupplierByName(selectedValue);
        
        if (foundSupplier) {
            updateSupplierField(foundSupplier.id, foundSupplier.name);
        } else {
            // Если введено что-то, что не в списке - очищаем
            if (selectedValue) {
                setTimeout(() => {
                    this.value = '';
                    updateSupplierField('', '');
                }, 100);
            }
        }
    });

    // Обработчик потери фокуса
    supplierSearch.addEventListener('blur', function() {
        setTimeout(() => {
            const currentValue = this.value;
            const foundSupplier = findSupplierByName(currentValue);
            
            if (currentValue && !foundSupplier) {
                this.value = '';
                updateSupplierField('', '');
                ComersApp.showNotification('Выберите поставщика из списка', 'warning');
            }
        }, 200);
    });

    // Кнопка очистки
    clearSearchBtn.addEventListener('click', function() {
        supplierSearch.value = '';
        updateSupplierField('', '');
        supplierSearch.focus();
    });

    // Кнопка показать все (кастомный dropdown)
    toggleListBtn.addEventListener('click', function() {
        if (customDropdown.style.display === 'none') {
            // Показываем dropdown
            customDropdown.style.display = 'block';
            
            // Заполняем dropdown
            dropdownOptions.innerHTML = '';
            allSuppliers.forEach(supplier => {
                const div = document.createElement('div');
                div.className = 'dropdown-option';
                div.textContent = supplier.name;
                div.dataset.id = supplier.id;
                div.dataset.name = supplier.name;
                
                div.addEventListener('click', function() {
                    supplierSearch.value = this.dataset.name;
                    updateSupplierField(this.dataset.id, this.dataset.name);
                    customDropdown.style.display = 'none';
                    supplierSearch.focus();
                });
                
                dropdownOptions.appendChild(div);
            });
            
            dropdownSearch.value = '';
            dropdownSearch.focus();
        } else {
            customDropdown.style.display = 'none';
        }
    });

    // Поиск в dropdown
    dropdownSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const options = dropdownOptions.querySelectorAll('.dropdown-option');
        
        options.forEach(option => {
            const name = option.dataset.name.toLowerCase();
            if (name.includes(searchTerm)) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });
    });

    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.form-group[style*="position: relative"]')) {
            customDropdown.style.display = 'none';
        }
    });

    // Инициализация: если есть значение в скрытом поле, устанавливаем соответствующий поставщик
    if (supplierHidden.value) {
        const supplier = allSuppliers.find(s => s.id === supplierHidden.value);
        if (supplier) {
            supplierSearch.value = supplier.name;
            updateSupplierField(supplier.id, supplier.name);
        }
    }
});