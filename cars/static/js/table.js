// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
const debounceTimers = {};
let pendingDeleteId = null;
let pendingParentId = null;
let childPreviewTimer = null;
let currentChildData = null;

// Базовый URL для API
const API_BASE = '/special_cars/';
const ARTICLE_SEARCH_URL = '/finder/get_details/article_id/';
const MIN_ARTICLE_LENGTH = 2;

let locationsList = [];
let saveTimers = {};

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || document.querySelector('[name=csrf-token]')?.content;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : 
                type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function updateStats() {
    const visibleRows = document.querySelectorAll('#table-body > tr[data-id]:not([style*="display: none"])');
    const totalCount = visibleRows.length;
    let totalQuantity = 0;
    visibleRows.forEach(row => {
        const quantity = parseInt(row.querySelector('.quantity-input')?.value) || 0;
        totalQuantity += quantity;
    });
    const totalCountEl = document.getElementById('total-count');
    const totalQuantityEl = document.getElementById('total-quantity');
    if (totalCountEl) totalCountEl.textContent = totalCount;
    if (totalQuantityEl) totalQuantityEl.textContent = totalQuantity;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== ПЕРЕКЛЮЧЕНИЕ ДОЧЕРНИХ ЭЛЕМЕНТОВ ==========

window.toggleChildren = function(parentId) {
    const children = document.querySelectorAll(`.child-row.parent-${parentId}`);
    const btn = document.querySelector(`tr[data-id="${parentId}"] .expand-btn i`);
    if (children.length === 0) return;
    
    const isHidden = children[0].style.display === 'none';
    children.forEach(child => child.style.display = isHidden ? '' : 'none');
    
    if (btn) {
        btn.className = isHidden ? 'fas fa-chevron-down' : 'fas fa-chevron-right';
    }
    updateStats();
};

// ========== СОХРАНЕНИЕ НА СЕРВЕР ==========

async function saveRowToServer(rowId, data) {
    const url = `${API_BASE}api/update-row/${rowId}/`;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCSRFToken() 
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        return response.ok && result.success;
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        return false;
    }
}

async function createNewRow(data, parentId = null) {
    const url = `${API_BASE}api/save-row/`;
    try {
        const requestData = {
            number: data.number || '',
            arrival_date: data.arrival_date || null,
            article: data.article || '',
            name: data.name || '',
            location: data.location || '',
            quantity: data.quantity || null,
            comment: data.comment || ''
        };
        if (parentId) {
            requestData.parent = parentId;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCSRFToken() 
            },
            body: JSON.stringify(requestData)
        });
        const result = await response.json();
        if (response.ok && result.success) {
            return result.id;
        }
        throw new Error(result.error || 'Ошибка создания');
    } catch (error) {
        console.error('Ошибка создания:', error);
        showToast(`Ошибка: ${error.message}`, 'error');
        return null;
    }
}

// ========== СОХРАНЕНИЕ ВСЕЙ СТРОКИ ==========

async function saveFullRow(rowId, showSaveToast = false) {
    const row = document.querySelector(`tr[data-id="${rowId}"]`);
    if (!row) return false;
    
    const data = {
        number: row.querySelector('.number-input')?.value || '',
        arrival_date: row.querySelector('.date-input')?.value || null,
        article: row.querySelector('.article-input')?.value || '',
        name: row.querySelector('.name-input')?.value || '',
        location: row.querySelector('.location-input')?.value || '',
        quantity: row.querySelector('.quantity-input')?.value || null,
        comment: row.querySelector('.comment-input')?.value || ''
    };
    
    const hasData = data.article || data.name || data.number || data.location || data.quantity || data.comment;
    if (!hasData) return false;
    
    if (rowId.toString().startsWith('new_')) {
        const parentId = row.getAttribute('data-parent');
        const newId = await createNewRow(data, parentId);
        if (newId) {
            row.setAttribute('data-id', newId);
            row.classList.remove('new-row');
            flashRowGreen(row);
            if (showSaveToast) showToast('✓ Строка создана', 'success');
            return true;
        }
        return false;
    }
    
    const success = await saveRowToServer(rowId, data);
    if (success) {
        flashRowGreen(row);
        if (showSaveToast) showToast('✓ Сохранено', 'success');
    }
    return success;
}

// ========== ВИЗУАЛЬНЫЙ ЭФФЕКТ СОХРАНЕНИЯ ==========

function flashRowGreen(row) {
    const inputs = row.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.style.transition = 'background-color 0.3s ease';
        input.style.backgroundColor = '#d1fae5';
        setTimeout(() => { 
            input.style.backgroundColor = ''; 
        }, 600);
    });
}

function flashFieldGreen(input) {
    input.style.transition = 'background-color 0.3s ease';
    input.style.backgroundColor = '#d1fae5';
    setTimeout(() => { 
        input.style.backgroundColor = ''; 
    }, 600);
}

// ========== ПОЛУЧЕНИЕ ID СТРОКИ ИЗ ЭЛЕМЕНТА ==========

function getRowId(element) {
    const row = element.closest('tr[data-id]');
    if (!row) return null;
    return row.getAttribute('data-id');
}

// ========== СОХРАНЕНИЕ ПОЛЯ (ЕДИНАЯ ФУНКЦИЯ) ==========

async function saveFieldHandler(input) {
    const rowId = getRowId(input);
    if (!rowId) return;
    
    const row = document.querySelector(`tr[data-id="${rowId}"]`);
    if (!row) return;
    
    const data = {
        number: row.querySelector('.number-input')?.value || '',
        arrival_date: row.querySelector('.date-input')?.value || null,
        article: row.querySelector('.article-input')?.value || '',
        name: row.querySelector('.name-input')?.value || '',
        location: row.querySelector('.location-input')?.value || '',
        quantity: row.querySelector('.quantity-input')?.value || null,
        comment: row.querySelector('.comment-input')?.value || ''
    };
    
    const hasData = data.article || data.name || data.number || data.location || data.quantity || data.comment;
    if (!hasData) return;
    
    if (rowId.startsWith('new_')) {
        const parentId = row.getAttribute('data-parent');
        const newId = await createNewRow(data, parentId);
        if (newId) {
            row.setAttribute('data-id', newId);
            row.classList.remove('new-row');
            flashFieldGreen(input);
            showToast('✓ Строка создана', 'success');
        }
        return;
    }
    
    const success = await saveRowToServer(rowId, data);
    if (success) {
        flashFieldGreen(input);
    }
}

// ========== ДЕЛЕГИРОВАНИЕ СОБЫТИЙ ==========

// Настраиваем делегирование для всех полей ввода
function setupDelegatedEvents() {
    const tableBody = document.getElementById('table-body');
    if (!tableBody) return;
    
    // Обработка ввода для всех полей (кроме date)
    tableBody.addEventListener('input', function(e) {
        const target = e.target;
        if (!target.matches('input:not([type="date"]), textarea')) return;
        
        const rowId = getRowId(target);
        if (!rowId) return;
        
        // Очищаем предыдущий таймер для этой строки
        if (saveTimers[rowId]) {
            clearTimeout(saveTimers[rowId]);
        }
        
        // Устанавливаем таймер с debounce
        saveTimers[rowId] = setTimeout(async () => {
            await saveFieldHandler(target);
        }, 500);
    });
    
    // Обработка для date (change)
    tableBody.addEventListener('change', function(e) {
        const target = e.target;
        if (!target.matches('input[type="date"]')) return;
        saveFieldHandler(target);
    });
    
    // Обработка для select
    tableBody.addEventListener('change', function(e) {
        const target = e.target;
        if (!target.matches('select')) return;
        saveFieldHandler(target);
        showToast('✓ Место сохранено', 'success');
    });
    
    // Обработка blur для всех полей
    tableBody.addEventListener('blur', function(e) {
        const target = e.target;
        if (!target.matches('input, select, textarea')) return;
        
        const rowId = getRowId(target);
        if (!rowId) return;
        
        // Очищаем таймер и сохраняем сразу
        if (saveTimers[rowId]) {
            clearTimeout(saveTimers[rowId]);
            delete saveTimers[rowId];
        }
        saveFieldHandler(target);
    }, true); // capture фаза для blur
    
    // Обработка Enter
    tableBody.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter') return;
        const target = e.target;
        if (!target.matches('input, select, textarea')) return;
        
        e.preventDefault();
        saveFieldHandler(target);
        
        // Переход на следующее поле
        const inputs = Array.from(document.querySelectorAll('.inventory-table input:not([readonly]), .inventory-table select'));
        const currentIndex = inputs.indexOf(target);
        if (currentIndex !== -1 && currentIndex < inputs.length - 1) {
            inputs[currentIndex + 1].focus();
        }
    });
}

// ========== АВТОПОДСТАНОВКА НАИМЕНОВАНИЯ ==========

window.autoFillName = async function(articleInput, rowId) {
    const article = articleInput.value.trim();
    const row = articleInput.closest('tr');
    const nameInput = row.querySelector('.name-input');
    const currentRowId = rowId.toString();
    
    if (debounceTimers[currentRowId]) clearTimeout(debounceTimers[currentRowId]);
    if (!article) {
        nameInput.value = '';
        nameInput.setAttribute('readonly', 'readonly');
        nameInput.placeholder = 'Наименование';
        nameInput.style.background = '#f9fafb';
        return;
    }
    if (article.length < MIN_ARTICLE_LENGTH) return;
    
    articleInput.classList.add('loading');
    nameInput.placeholder = 'Поиск...';
    nameInput.style.background = '#fff8e1';
    
    debounceTimers[currentRowId] = setTimeout(async () => {
        try {
            const response = await fetch(`${ARTICLE_SEARCH_URL}${encodeURIComponent(article)}/`);
            if (response.ok) {
                const data = await response.json();
                if (data && data.title) {
                    nameInput.value = data.title;
                    nameInput.classList.add('auto-filled');
                    setTimeout(() => nameInput.classList.remove('auto-filled'), 500);
                    nameInput.setAttribute('readonly', 'readonly');
                    nameInput.placeholder = 'Наименование';
                    nameInput.style.background = '#f9fafb';
                    showToast(`✓ Найдено: ${data.title}`, 'success');
                    
                    // Сохраняем через общий обработчик
                    await saveFieldHandler(articleInput);
                    flashFieldGreen(nameInput);
                }
            } else {
                nameInput.value = '';
                nameInput.placeholder = 'Артикул не найден, введите вручную';
                nameInput.removeAttribute('readonly');
                nameInput.style.background = '#fff3e0';
                nameInput.style.border = '1px solid #ff9800';
                showToast(`⚠ Артикул "${article}" не найден. Введите наименование вручную.`, 'info');
                
                await saveFieldHandler(articleInput);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            nameInput.placeholder = 'Ошибка поиска, введите вручную';
            nameInput.removeAttribute('readonly');
            nameInput.style.background = '#fff3e0';
            showToast('❌ Ошибка поиска. Введите наименование вручную.', 'error');
        } finally {
            articleInput.classList.remove('loading');
            updateStats();
        }
    }, 1000);
};

// ========== ДОБАВЛЕНИЕ ДОЧЕРНЕЙ ПОЗИЦИИ ==========

window.showAddChildModal = function(parentId, parentName) {
    if (parentId.toString().startsWith('new_')) {
        showToast('Сначала сохраните основную позицию', 'error');
        return;
    }
    pendingParentId = parentId;
    currentChildData = null;
    document.getElementById('parent-name').textContent = parentName || 'этой позиции';
    document.getElementById('child-article').value = '';
    document.getElementById('child-quantity').value = '1';
    document.getElementById('child-article-preview').innerHTML = '';
    document.getElementById('addChildModal').style.display = 'flex';
    setTimeout(() => document.getElementById('child-article').focus(), 100);
};

window.closeChildModal = function() {
    document.getElementById('addChildModal').style.display = 'none';
    pendingParentId = null;
    currentChildData = null;
    if (childPreviewTimer) clearTimeout(childPreviewTimer);
};

async function searchChildArticle(article) {
    const previewDiv = document.getElementById('child-article-preview');
    if (article.length < MIN_ARTICLE_LENGTH) {
        previewDiv.innerHTML = `<span style="color: #9ca3af;">Введите минимум ${MIN_ARTICLE_LENGTH} символа...</span>`;
        currentChildData = null;
        return;
    }
    
    previewDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Поиск...';
    try {
        const response = await fetch(`${ARTICLE_SEARCH_URL}${encodeURIComponent(article)}/`);
        if (response.ok) {
            const data = await response.json();
            currentChildData = data;
            previewDiv.innerHTML = `
                <div style="background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; padding: 8px 12px; margin-top: 4px;">
                    <i class="fas fa-check-circle" style="color: #10b981;"></i> 
                    Найдено: <strong>${escapeHtml(data.title)}</strong>
                </div>
            `;
        } else {
            currentChildData = null;
            previewDiv.innerHTML = `
                <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 8px 12px; margin-top: 4px;">
                    <i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i> 
                    Артикул не найден
                </div>
            `;
        }
    } catch (error) {
        previewDiv.innerHTML = `
            <div style="background: #fee2e2; border: 1px solid #ef4444; border-radius: 8px; padding: 8px 12px; margin-top: 4px;">
                <i class="fas fa-times-circle" style="color: #ef4444;"></i> 
                Ошибка поиска
            </div>
        `;
    }
}

window.addChildItem = async function() {
    const article = document.getElementById('child-article').value.trim();
    const quantity = document.getElementById('child-quantity').value;
    
    if (!article) {
        showToast('Введите артикул', 'error');
        return;
    }
    
    const addBtn = document.querySelector('#addChildModal .btn-primary');
    const originalText = addBtn.innerHTML;
    addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Добавление...';
    addBtn.disabled = true;
    
    try {
        let name = currentChildData?.title || article;
        const requestData = {
            parent_id: pendingParentId,
            article: article,
            name: name,
            quantity: parseInt(quantity) || 1
        };
        
        const response = await fetch(`${API_BASE}api/add-child/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCSRFToken() 
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        if (response.ok && result.success) {
            showToast(`✓ "${name}" добавлена`, 'success');
            location.reload();
        } else {
            throw new Error(result.error || 'Ошибка добавления');
        }
    } catch (error) {
        showToast(`❌ Ошибка: ${error.message}`, 'error');
    } finally {
        addBtn.innerHTML = originalText;
        addBtn.disabled = false;
        closeChildModal();
    }
};

// ========== ДОБАВЛЕНИЕ НОВОЙ СТРОКИ ==========

window.addNewRow = function() {
    const tbody = document.getElementById('table-body');
    const noDataRow = document.getElementById('no-data-row');
    if (noDataRow) noDataRow.remove();
    
    const newId = 'new_' + Date.now();
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-id', newId);
    newRow.setAttribute('data-parent', '');
    newRow.setAttribute('data-level', '0');
    newRow.classList.add('new-row');
    
    let locationOptions = '<option value="">-- Выберите место --</option>';
    locationsList.forEach(loc => { 
        locationOptions += `<option value="${loc}">${loc}</option>`; 
    });
    
    newRow.innerHTML = `
        <td class="expand-cell" style="text-align: center;"></td>
        <td><input type="text" class="number-input" placeholder="Введите №" data-field="number"></td>
        <td><input type="date" class="date-input" placeholder="дд.мм.гггг" data-field="arrival_date"></td>
        <td><input type="text" class="article-input" placeholder="Введите артикул" data-field="article" oninput="autoFillName(this, '${newId}')"></td>
        <td><input type="text" class="name-input" readonly style="background:#f9fafb; width:100%; min-width:100px;" placeholder="Наименование" data-field="name"></td>
        <td><select class="location-input" data-field="location">${locationOptions}</select></td>
        <td><input type="number" class="quantity-input" placeholder="0" data-field="quantity"></td>
        <td><input type="text" class="comment-input" placeholder="Комментарий" data-field="comment"></td>
        <td class="delete-cell">
            <div class="action-buttons">
                <button class="add-child-btn" onclick="showAddChildModal('${newId}', '')" title="Добавить комплектующую">
                    <i class="fas fa-plus-circle"></i>
                </button>
                <button class="delete-btn" onclick="showDeleteModal('${newId}')">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        </td>
    `;
    
    tbody.appendChild(newRow);
    
    showToast('➕ Новая строка добавлена', 'info');
    newRow.querySelector('.article-input').focus();
    updateStats();
};

// ========== УДАЛЕНИЕ ==========

window.showDeleteModal = function(rowId) {
    pendingDeleteId = rowId;
    document.getElementById('deleteModal').style.display = 'flex';
};

window.closeDeleteModal = function() {
    document.getElementById('deleteModal').style.display = 'none';
    pendingDeleteId = null;
};

window.confirmDelete = async function() {
    if (!pendingDeleteId) return;
    
    if (pendingDeleteId.toString().startsWith('new_')) {
        const row = document.querySelector(`tr[data-id="${pendingDeleteId}"]`);
        if (row) row.remove();
        showToast('✓ Строка удалена', 'success');
        updateStats();
        closeDeleteModal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}api/delete-row/${pendingDeleteId}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCSRFToken() }
        });
        if (response.ok) {
            showToast('✓ Запись удалена', 'success');
            location.reload();
        } else {
            showToast('❌ Ошибка при удалении', 'error');
        }
    } catch (error) {
        showToast('❌ Ошибка при удалении', 'error');
    }
    closeDeleteModal();
};

// ========== ФИЛЬТРАЦИЯ (ПОИСК) ==========

window.filterTable = function() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase().trim();
    const clearBtn = document.querySelector('.search-clear');
    if (clearBtn) {
        clearBtn.style.display = searchTerm ? 'flex' : 'none';
    }
    
    const allRows = document.querySelectorAll('#table-body > tr[data-id]');
    const childRows = document.querySelectorAll('.child-row');
    
    if (searchTerm === '') {
        allRows.forEach(row => row.style.display = '');
        childRows.forEach(child => child.style.display = 'none');
        document.querySelectorAll('.expand-btn i').forEach(icon => {
            icon.className = 'fas fa-chevron-right';
        });
        const searchNoData = document.getElementById('search-no-data');
        if (searchNoData) searchNoData.remove();
        updateStats();
        return;
    }
    
    childRows.forEach(child => child.style.display = 'none');
    
    let visibleCount = 0;
    let foundIds = new Set();
    
    allRows.forEach(row => {
        const number = row.querySelector('.number-input')?.value || '';
        const article = row.querySelector('.article-input')?.value || '';
        const name = row.querySelector('.name-input')?.value || '';
        const location = row.querySelector('.location-input')?.value || '';
        const comment = row.querySelector('.comment-input')?.value || '';
        
        const fullText = `${number} ${article} ${name} ${location} ${comment}`.toLowerCase();
        const matches = fullText.includes(searchTerm);
        const rowId = row.getAttribute('data-id');
        
        if (matches) {
            row.style.display = '';
            visibleCount++;
            foundIds.add(rowId);
            
            let parentId = row.getAttribute('data-parent');
            while (parentId && parentId !== '' && parentId !== 'null') {
                const parentRow = document.querySelector(`tr[data-id="${parentId}"]`);
                if (parentRow) {
                    parentRow.style.display = '';
                    foundIds.add(parentId);
                    
                    const children = document.querySelectorAll(`.child-row.parent-${parentId}`);
                    children.forEach(child => {
                        child.style.display = '';
                        foundIds.add(child.getAttribute('data-id'));
                    });
                    
                    const btn = parentRow.querySelector('.expand-btn i');
                    if (btn) btn.className = 'fas fa-chevron-down';
                }
                parentId = parentRow?.getAttribute('data-parent');
            }
        } else if (!row.classList.contains('child-row')) {
            const hasVisibleChildren = row.querySelectorAll('.child-row:not([style*="display: none"])').length > 0;
            if (!hasVisibleChildren) {
                row.style.display = 'none';
            }
        }
    });
    
    const searchNoData = document.getElementById('search-no-data');
    if (searchNoData) searchNoData.remove();
    
    if (visibleCount === 0 && allRows.length > 0) {
        const tbody = document.getElementById('table-body');
        const emptyRow = document.createElement('tr');
        emptyRow.id = 'search-no-data';
        emptyRow.innerHTML = `
            <td colspan="9">
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>Ничего не найдено</p>
                    <p style="font-size: 12px;">Попробуйте изменить поисковый запрос</p>
                </div>
            </td>
        `;
        tbody.appendChild(emptyRow);
    }
    
    updateStats();
};

window.clearSearch = function() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
        filterTable();
        searchInput.focus();
    }
};

// ========== ЗАГРУЗКА ЛОКАЦИЙ ==========

async function loadLocations() {
    try {
        const response = await fetch(`${API_BASE}api/get-locations/`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) locationsList = data.locations;
        }
    } catch (error) {
        console.error('Ошибка загрузки локаций:', error);
    }
}

// ========== ЭКСПОРТ ОТЧЕТА ==========

function exportReport() {
    showToast('📊 Формирование отчета...', 'info');
    const link = document.createElement('a');
    link.href = '/special_cars/export-report/';
    link.download = 'inventory_report.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => {
        showToast('✅ Отчет скачан', 'success');
    }, 1500);
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== СТРАНИЦА ЗАГРУЖЕНА ===');
    loadLocations();
    updateStats();
    
    // Настраиваем делегирование событий
    setupDelegatedEvents();
    
    // Автоподстановка в модальном окне
    const childInput = document.getElementById('child-article');
    if (childInput) {
        childInput.addEventListener('input', function() {
            if (childPreviewTimer) clearTimeout(childPreviewTimer);
            childPreviewTimer = setTimeout(() => searchChildArticle(this.value.trim()), 500);
        });
    }
    
    // Модальные окна
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('click', function(e) {
            if (e.target === this) closeDeleteModal();
        });
    }
    
    const childModal = document.getElementById('addChildModal');
    if (childModal) {
        childModal.addEventListener('click', function(e) {
            if (e.target === this) closeChildModal();
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeDeleteModal();
            closeChildModal();
        }
    });
    
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (confirmBtn) confirmBtn.onclick = confirmDelete;
});