// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
const debounceTimers = {};

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

// Получение CSRF токена
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || document.querySelector('[name=csrf-token]')?.content;
}

// Показ уведомления
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 
                type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Обновление статистики
function updateStats() {
    const rows = document.querySelectorAll('#table-body tr[data-id]');
    const totalCount = rows.length;
    
    let totalQuantity = 0;
    rows.forEach(row => {
        const quantity = parseInt(row.querySelector('.quantity-input')?.value) || 0;
        totalQuantity += quantity;
    });
    
    const totalCountEl = document.getElementById('total-count');
    const totalQuantityEl = document.getElementById('total-quantity');
    
    if (totalCountEl) totalCountEl.textContent = totalCount;
    if (totalQuantityEl) totalQuantityEl.textContent = totalQuantity;
}

// Сохранение строки на сервер
async function saveRowToServer(rowId) {
    const row = document.querySelector(`tr[data-id="${rowId}"]`);
    if (!row || rowId.toString().startsWith('new_')) return;
    
    const data = {
        number: row.querySelector('.number-input')?.value || '',
        arrival_date: row.querySelector('.date-input')?.value || null,
        article: row.querySelector('.article-input')?.value || '',
        name: row.querySelector('.name-input')?.value || '',
        quantity: row.querySelector('.quantity-input')?.value || null,
        unit: row.querySelector('.unit-input')?.value || '',
        comment: row.querySelector('.comment-input')?.value || ''
    };
    
    try {
        const response = await fetch(`/api/update-row/${rowId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка сохранения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showToast('Ошибка при сохранении', 'error');
    }
}

// Автосохранение с debounce
let saveTimeout;

function autoSave(rowId) {
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveRowToServer(rowId);
    }, 1000);
}

// ========== ОСНОВНЫЕ ФУНКЦИИ ==========

// Автоподстановка наименования через API
window.autoFillName = async function(articleInput, rowId) {
    const article = articleInput.value.trim();
    const row = articleInput.closest('tr');
    const nameInput = row.querySelector('.name-input');
    const unitInput = row.querySelector('.unit-input');
    
    // Очищаем предыдущий таймер
    if (debounceTimers[rowId]) {
        clearTimeout(debounceTimers[rowId]);
    }
    
    // Если артикул пустой, очищаем наименование
    if (!article) {
        nameInput.value = '';
        return;
    }
    
    // Показываем индикатор загрузки
    articleInput.classList.add('loading');
    
    // Устанавливаем задержку 500мс перед запросом
    debounceTimers[rowId] = setTimeout(async () => {
        try {
            // Пробуем разные варианты URL
            let data = null;
            let found = false;
            
            // Список URL для попытки
            const urlsToTry = [
                // Прямой URL с артикулом (без кодирования)
                `/finder/get_details/article_id/${article}/`,
                // Закодированный URL
                `/finder/get_details/article_id/${encodeURIComponent(article)}/`,
            ];
            
            // Пробуем каждый URL
            for (const url of urlsToTry) {
                try {
                    console.log('Пробуем URL:', url);
                    const response = await fetch(url);
                    
                    if (response.ok) {
                        data = await response.json();
                        found = true;
                        console.log('Успешно! Данные:', data);
                        break;
                    } else if (response.status === 404) {
                        console.log('URL вернул 404:', url);
                    }
                } catch (e) {
                    console.log('Ошибка при запросе к URL:', url, e);
                }
            }
            
            // Если нашли данные
            if (found && data && data.title) {
                // Подставляем наименование
                nameInput.value = data.title;
                nameInput.classList.add('auto-filled');
                setTimeout(() => nameInput.classList.remove('auto-filled'), 500);
                
                // Подставляем единицу измерения если есть
                if (data.base_unit && unitInput && !unitInput.value) {
                    unitInput.value = data.base_unit;
                }
                
                showToast(`✓ Найдено: ${data.title}`, 'success');
                
                // Сохраняем дополнительные данные в атрибуты строки
                row.setAttribute('data-article-id', data.id);
                row.setAttribute('data-total-quantity', data.total_quantity || 0);
                
                // Автосохраняем строку если это существующая запись
                if (!rowId.toString().startsWith('new_')) {
                    saveRowToServer(rowId);
                }
            } else {
                // Артикул не найден
                nameInput.value = '';
                showToast(`✗ Артикул "${article}" не найден`, 'error');
            }
        } catch (error) {
            console.error('Критическая ошибка:', error);
            nameInput.value = '';
            showToast('❌ Ошибка подключения к серверу', 'error');
        } finally {
            // Убираем индикатор загрузки
            articleInput.classList.remove('loading');
            updateStats();
        }
    }, 500);
};

// Добавление новой строки
window.addNewRow = function() {
    const tbody = document.getElementById('table-body');
    const noDataRow = document.getElementById('no-data-row');
    if (noDataRow) noDataRow.remove();
    
    const newId = 'new_' + Date.now();
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-id', newId);
    
    newRow.innerHTML = `
        <td><input type="text" class="number-input" placeholder="Введите № ТН/ТТН"></td>
        <td><input type="date" class="date-input"></td>
        <td>
            <input type="text" 
                   class="article-input" 
                   placeholder="Введите артикул"
                   oninput="autoFillName(this, '${newId}')">
        </td>
        <td><input type="text" class="name-input" readonly style="background:#f9fafb"></td>
        <td><input type="number" class="quantity-input" placeholder="0"></td>
        <td><input type="text" class="unit-input" placeholder="шт"></td>
        <td><input type="text" class="comment-input" placeholder="Комментарий"></td>
        <td class="delete-cell">
            <button class="delete-btn" onclick="deleteNewRow(this)">
                <i class="fas fa-trash-alt"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(newRow);
    showToast('➕ Новая строка добавлена', 'info');
    newRow.querySelector('.article-input').focus();
    updateStats();
};

// Удаление существующей строки
window.deleteRow = async function(rowId) {
    if (!confirm('Вы уверены, что хотите удалить эту запись?')) return;
    
    try {
        const response = await fetch(`/api/delete-row/${rowId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (response.ok) {
            const row = document.querySelector(`tr[data-id="${rowId}"]`);
            if (row) row.remove();
            showToast('✓ Запись удалена', 'success');
            
            // Проверяем, остались ли строки
            if (document.getElementById('table-body').children.length === 0) {
                document.getElementById('table-body').innerHTML = `
                    <tr id="no-data-row">
                        <td colspan="8">
                            <div class="empty-state">
                                <i class="fas fa-inbox"></i>
                                <p>Нет данных</p>
                                <p style="font-size: 12px; margin-top: 8px;">Нажмите кнопку "Добавить строку" чтобы начать</p>
                            </div>
                        </td>
                    </tr>
                `;
            }
            updateStats();
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showToast('❌ Ошибка при удалении', 'error');
    }
};

// Удаление новой (несохраненной) строки
window.deleteNewRow = function(button) {
    const row = button.closest('tr');
    row.remove();
    showToast('✓ Строка удалена', 'success');
    
    // Проверяем, остались ли строки
    if (document.getElementById('table-body').children.length === 0) {
        document.getElementById('table-body').innerHTML = `
            <tr id="no-data-row">
                <td colspan="8">
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>Нет данных</p>
                        <p style="font-size: 12px; margin-top: 8px;">Нажмите кнопку "Добавить строку" чтобы начать</p>
                    </div>
                </td>
            </tr>
        `;
    }
    updateStats();
};

// Функция для тестирования API (в консоли)
window.testAPI = async function(article) {
    console.log('=== ТЕСТИРОВАНИЕ API ===');
    console.log('Артикул:', article);
    
    try {
        // Пробуем разные варианты
        const urls = [
            `/finder/get_details/article_id/${article}/`,
            `/finder/get_details/article_id/${encodeURIComponent(article)}/`,
        ];
        
        for (const url of urls) {
            console.log(`\nПробуем URL: ${url}`);
            try {
                const response = await fetch(url);
                console.log(`Статус: ${response.status}`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('УСПЕХ! Данные:', data);
                    console.log('Название (title):', data.title);
                    console.log('Ед. изм. (base_unit):', data.base_unit);
                    showToast(`✓ Найдено: ${data.title}`, 'success');
                    return data;
                } else if (response.status === 404) {
                    console.log('❌ 404 - не найдено');
                }
            } catch (e) {
                console.log('❌ Ошибка запроса:', e.message);
            }
        }
        
        console.log('❌ Артикул не найден ни по одному из URL');
        showToast(`✗ Артикул "${article}" не найден`, 'error');
        return null;
        
    } catch (error) {
        console.error('❌ Критическая ошибка:', error);
        showToast('Ошибка при запросе к API', 'error');
        return null;
    }
};

// Функция для просмотра всех артикулов в базе
window.showAllArticles = async function() {
    console.log('=== ПОЛУЧЕНИЕ ВСЕХ АРТИКУЛОВ ===');
    try {
        // Этот эндпоинт нужно добавить на бэкенде
        const response = await fetch('/api/get-all-articles/');
        if (response.ok) {
            const data = await response.json();
            console.log('Все артикулы:', data);
            return data;
        } else {
            console.log('API для получения всех артикулов не настроен');
            console.log('Попробуйте использовать testAPI("конкретный_артикул")');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
};

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== СТРАНИЦА ЗАГРУЖЕНА ===');
    updateStats();
    
    // Автосохранение при изменении полей
    document.addEventListener('input', function(e) {
        const row = e.target.closest('tr');
        if (row && row.getAttribute('data-id') && !row.getAttribute('data-id').startsWith('new_')) {
            const rowId = row.getAttribute('data-id');
            autoSave(rowId);
        }
        updateStats();
    });
    
    // Поддержка Enter для перехода к следующему полю
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const inputs = Array.from(document.querySelectorAll('.inventory-table input:not([readonly])'));
            const currentIndex = inputs.indexOf(e.target);
            if (currentIndex !== -1 && inputs[currentIndex + 1]) {
                e.preventDefault();
                inputs[currentIndex + 1].focus();
            }
        }
    });
    
    // Добавляем иконки в поля ввода
    document.querySelectorAll('.inventory-table td').forEach(td => {
        const input = td.querySelector('input');
        if (!input) return;
        
        input.style.paddingLeft = '32px';
        td.style.position = 'relative';
        
        let icon = '';
        if (input.classList.contains('number-input')) icon = 'fa-hashtag';
        else if (input.classList.contains('date-input')) icon = 'fa-calendar';
        else if (input.classList.contains('article-input')) icon = 'fa-barcode';
        else if (input.classList.contains('name-input')) icon = 'fa-tag';
        else if (input.classList.contains('quantity-input')) icon = 'fa-cubes';
        else if (input.classList.contains('unit-input')) icon = 'fa-ruler';
        else if (input.classList.contains('comment-input')) icon = 'fa-comment';
        
        if (icon) {
            const iconSpan = document.createElement('i');
            iconSpan.className = `fas ${icon}`;
            iconSpan.style.cssText = `
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                color: #9ca3af;
                font-size: 12px;
                pointer-events: none;
                z-index: 1;
            `;
            td.insertBefore(iconSpan, input);
        }
    });
    
    console.log('Доступные команды в консоли:');
    console.log('  testAPI("артикул") - проверить API для конкретного артикула');
    console.log('  showAllArticles() - показать все артикулы (если API настроен)');
});