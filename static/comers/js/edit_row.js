// static/comers/js/edit_row.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    // Делегирование событий для загрузки данных при открытии попапа редактирования
    document.addEventListener('click', async function(e) {
        // Клик по кнопке "Редактировать" в таблице
        if (e.target.closest('.open-btn[data-popup="popup5"]') || 
            e.target.closest('.edit_button')) {
            
            // Находим кнопку и ID
            const button = e.target.closest('.edit_button') || 
                          e.target.closest('.open-btn[data-popup="popup5"]').closest('.edit_button');
            
            if (button && button.dataset.id) {
                const invoiceId = button.dataset.id;
                console.log('Загрузка данных для редактирования ID:', invoiceId);
                
                ComersApp.setCurrentEditId(invoiceId);
                
                try {
                    // Загружаем данные с сервера через правильный эндпоинт
                    const data = await ComersApp.fetchData(`/comers/edit_invoices/${invoiceId}/`);
                    console.log('Получены данные для редактирования:', data);
                    
                    // Заполняем форму редактирования
                    const form = document.getElementById('editInvoiceForm');
                    if (form) {
                        // Заполняем основные поля
                        const fieldsToFill = [
                            'invoice_number',
                            'date',
                            'name',
                            'quantity',
                            'description_problem',
                            'article',
                            'unit',
                            'description'
                        ];
                        
                        fieldsToFill.forEach(fieldName => {
                            const input = form.querySelector(`[name="${fieldName}"]`);
                            if (input && data[fieldName] !== undefined) {
                                input.value = data[fieldName] || '';
                            }
                        });
                        
                        // Заполняем поля с ForeignKey
                        const fkFields = [
                            { field: 'supplier', data: data.supplier },
                            { field: 'comment', data: data.comment },
                            { field: 'specialist', data: data.specialist },
                            { field: 'leading', data: data.leading },
                            { field: 'status', data: data.status },
                            { field: 'project', data: data.project }
                        ];
                        
                        fkFields.forEach(({ field, data: fieldData }) => {
                            const select = form.querySelector(`[name="${field}"]`);
                            if (select && fieldData) {
                                select.value = typeof fieldData === 'object' ? fieldData.id : fieldData;
                            }
                        });
                        
                        // Скрытые поля
                        const hiddenFields = ['article', 'unit', 'project'];
                        hiddenFields.forEach(fieldName => {
                            const hiddenInput = form.querySelector(`input[name="${fieldName}"]`);
                            if (hiddenInput && data[fieldName]) {
                                hiddenInput.value = data[fieldName];
                            }
                        });
                    }
                    
                } catch (error) {
                    console.error('Ошибка загрузки данных:', error);
                    ComersApp.showNotification('Ошибка загрузки данных для редактирования', 'error');
                }
            }
        }
        
        // Клик по кнопке "Статус" в таблице
        if (e.target.closest('.open-btn[data-popup="popup6"]') || 
            e.target.closest('.edit_status_button')) {
            
            const button = e.target.closest('.edit_status_button') || 
                          e.target.closest('.open-btn[data-popup="popup6"]').closest('.edit_status_button');
            
            if (button && button.dataset.id) {
                const invoiceId = button.dataset.id;
                console.log('Загрузка данных для статуса ID:', invoiceId);
                
                ComersApp.setCurrentEditId(invoiceId);
                
                try {
                    // Загружаем данные с сервера через правильный эндпоинт
                    const data = await ComersApp.fetchData(`/comers/edit_invoices/${invoiceId}/`);
                    
                    // Заполняем форму статуса
                    const form = document.getElementById('editInvoiceFormStatus');
                    if (form) {
                        // Поле статуса
                        const statusSelect = form.querySelector('select[name="status"]');
                        if (statusSelect && data.status) {
                            statusSelect.value = typeof data.status === 'object' ? data.status.id : data.status;
                        }
                        
                        // Поле описания
                        const descriptionInput = form.querySelector('textarea[name="description"], input[name="description"]');
                        if (descriptionInput) {
                            descriptionInput.value = data.description || '';
                        }
                    }
                    
                } catch (error) {
                    console.error('Ошибка загрузки данных для статуса:', error);
                    ComersApp.showNotification('Ошибка загрузки данных для статуса', 'error');
                }
            }
        }
    });
});