document.addEventListener('DOMContentLoaded', function() {
    fetch('/comers/get_all_positions/')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('invoiceTableBody');
            console.log(data)
            tableBody.innerHTML = ''; // Очищаем таблицу

            data.forEach(item => {
                const row = document.createElement('tr');

                // Извлекаем текстовые значения из вложенных объектов
                const commentText = item.comment ? item.comment.text : '';
                const leadingName = item.leading ? item.leading.name : '';
                const specialistName = item.specialist ? item.specialist.name : '';
                const statusName = item.status ? item.status.name : '';
                const supplierName = item.supplier ? item.supplier.name : '';

                row.innerHTML = `
                <td hidden class="id-cell">${item.id || ''}</td>
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
        })
        .catch(error => {
            console.error('Error fetching positions:', error);
        });
});
