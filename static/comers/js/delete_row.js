// static/comers/js/delete_row.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что ComersApp загружен
    if (typeof ComersApp === 'undefined') {
        console.error('ComersApp не загружен');
        return;
    }
    
    const deleteButton = document.getElementById('del_row_comers_table');
    if (!deleteButton) return;
    
    deleteButton.addEventListener('click', async function() {
        const currentDeleteId = ComersApp.getCurrentDeleteId();
        console.log('Попытка удаления ID:', currentDeleteId);
        
        if (!currentDeleteId) {
            ComersApp.showNotification('ID для удаления не найден', 'error');
            return;
        }
        
        // Показываем индикатор загрузки
        const originalText = deleteButton.textContent;
        deleteButton.textContent = 'Удаление...';
        deleteButton.disabled = true;
        
        try {
            const response = await fetch(`/comers/remove_position/${currentDeleteId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': ComersApp.getCsrfToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Удаляем строку из таблицы с анимацией
                const removed = ComersApp.removeRowFromTable(currentDeleteId);
                
                if (removed) {
                    console.log('Строка удалена из DOM');
                    
                    // Закрываем попап
                    ComersApp.closeActivePopup();
                    
                    ComersApp.showNotification('Позиция успешно удалена', 'success');
                    
                    // Обновляем данные
                    const allData = ComersApp.getAllData();
                    const filteredData = allData.filter(item => item.id != currentDeleteId);
                    ComersApp.setAllData(filteredData);
                    ComersApp.setFilteredData([...filteredData]);
                    
                } else {
                    ComersApp.showNotification('Строка не найдена в таблице', 'warning');
                }
                
            } else {
                throw new Error(data.error || 'Ошибка при удалении');
            }
            
        } catch (error) {
            console.error('Ошибка при удалении:', error);
            ComersApp.showNotification('Ошибка при удалении: ' + error.message, 'error');
            
        } finally {
            // Восстанавливаем кнопку
            deleteButton.textContent = originalText;
            deleteButton.disabled = false;
            ComersApp.setCurrentDeleteId(null);
        }
    });
    
    // Дополнительно: обработчик для кнопки удаления в таблице (делегирование)
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete_button')) {
            const deleteBtn = e.target.closest('.delete_button');
            const invoiceId = deleteBtn.dataset.id;
            
            if (invoiceId) {
                ComersApp.setCurrentDeleteId(invoiceId);
                console.log('ID для удаления установлен из таблицы:', invoiceId);
            }
        }
    });
});