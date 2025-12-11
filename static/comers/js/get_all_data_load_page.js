// static/comers/js/get_all_data_load_page.js
document.addEventListener('DOMContentLoaded', async function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        // Создаем временный fallback
        window.ComersApp = {
            showNotification: function(msg, type) {
                console.log(`${type}: ${msg}`);
            },
            loadAllData: async function() {
                try {
                    const response = await fetch('/comers/get_all_positions/');
                    const data = await response.json();
                    
                    // Простая отрисовка таблицы если ComersApp не работает
                    const tableBody = document.getElementById('invoiceTableBody');
                    if (tableBody) {
                        tableBody.innerHTML = '';
                        data.forEach(item => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${item.invoice_number || ''}</td>
                                <td>${item.date || ''}</td>
                                <td>${item.supplier?.name || ''}</td>
                                <td>${item.article || ''}</td>
                                <td>${item.name || ''}</td>
                                <td>${item.unit || ''}</td>
                                <td>${item.quantity || ''}</td>
                                <td>${item.comment?.text || ''}</td>
                                <td>${item.description_problem || ''}</td>
                                <td>${item.specialist?.name || ''}</td>
                                <td>${item.leading?.name || ''}</td>
                                <td>${item.status?.name || ''}</td>
                                <td>${item.description || ''}</td>
                                <td>
                                    <div class="action_cell_table">
                                        <div class="edit_invoice_button edit_button" data-id="${item.id}">
                                            <img src="/static/comers/icons/icon_edit.png" alt="Редактировать">
                                            <div class="open-btn" data-popup="popup5">Редактировать</div>
                                        </div>
                                        <div class="edit_invoice_button edit_status_button" data-id="${item.id}">
                                            <img src="/static/comers/icons/icon_status.png" alt="Статус">
                                            <div class="open-btn" data-popup="popup6">Статус</div>
                                        </div>
                                        <div class="edit_invoice_button delete_button" data-id="${item.id}">
                                            <img src="/static/comers/icons/icon_delete.png" alt="Удалить">
                                            <div class="open-btn" data-popup="popup7">Удалить</div>
                                        </div>
                                    </div>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });
                    }
                } catch (error) {
                    console.error('Ошибка загрузки данных:', error);
                }
            }
        };
    }
    
    // Загружаем все данные при старте
    try {
        await ComersApp.loadAllData();
        console.log('Данные загружены успешно');
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
});