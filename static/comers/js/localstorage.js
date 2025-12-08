document.addEventListener('DOMContentLoaded', function() {
    const supplierSelect = document.getElementById('id_supplier');
    const leadingSelect = document.getElementById('id_leading');
    const statusSelect = document.getElementById('id_status');

    // Функция для фильтрации данных
    function filterTable() {
        const selectedSupplier = supplierSelect.value;
        const selectedLeading = leadingSelect.value;
        const selectedStatus = statusSelect.value;

        fetch('/comers/get_all_positions/')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById('invoiceTableBody');
                tableBody.innerHTML = '';

                data.forEach(item => {
                    const supplierName = item.supplier ? item.supplier.name : '';
                    const leadingName = item.leading ? item.leading.name : '';
                    const statusName = item.status ? item.status.name : '';

                    // Проверяем, соответствует ли элемент выбранным фильтрам
                    const matchesSupplier = !selectedSupplier || (item.supplier && item.supplier.id == selectedSupplier);
                    const matchesLeading = !selectedLeading || (item.leading && item.leading.id == selectedLeading);
                    const matchesStatus = !selectedStatus || (item.status && item.status.id == selectedStatus);

                    if (matchesSupplier && matchesLeading && matchesStatus) {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${item.invoice_number || ''}</td>
                            <td>${item.date || ''}</td>
                            <td>${supplierName}</td>
                            <!-- остальные ячейки -->
                        `;
                        tableBody.appendChild(row);
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching positions:', error);
            });
    }

    // Добавляем обработчики событий
    supplierSelect.addEventListener('change', filterTable);
    leadingSelect.addEventListener('change', filterTable);
    statusSelect.addEventListener('change', filterTable);

    // Первоначальная загрузка данных
    filterTable();
});
