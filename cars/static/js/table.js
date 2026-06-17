// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
const debounceTimers = {};
let pendingDeleteId = null;
let pendingParentId = null;
let childPreviewTimer = null;
let currentChildData = null;

// Базовый URL для API - исправлено для вашего приложения
const API_BASE = '/special_cars/';
const ARTICLE_SEARCH_URL = '/finder/get_details/article_id/';
const MIN_ARTICLE_LENGTH = 2;

let locationsList = [];

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
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        return response.ok && result.success;
    } catch (error) {
        console.error('Ошибка:', error);
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
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
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

async function saveField(rowId, fieldName, value) {
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
    return await saveRowToServer(rowId, data);
}

// ========== АВТОСОХРАНЕНИЕ ==========

function setupAutoSave(input, rowId, fieldName) {
    input.addEventListener('blur', async function() {
        if (rowId.toString().startsWith('new_')) return;
        const success = await saveField(rowId, fieldName, this.value);
        if (success) {
            this.style.backgroundColor = '#d1fae5';
            setTimeout(() => { this.style.backgroundColor = ''; }, 300);
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
        return;
    }
    if (article.length < MIN_ARTICLE_LENGTH) return;
    
    articleInput.classList.add('loading');
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
                    showToast(`✓ Найдено: ${data.title}`, 'success');
                    
                    if (currentRowId.startsWith('new_')) {
                        const parentId = row.getAttribute('data-parent');
                        const rowData = {
                            number: row.querySelector('.number-input')?.value || '',
                            arrival_date: row.querySelector('.date-input')?.value || null,
                            article: article,
                            name: data.title,
                            location: row.querySelector('.location-input')?.value || '',
                            quantity: row.querySelector('.quantity-input')?.value || null,
                            comment: row.querySelector('.comment-input')?.value || ''
                        };
                        const newId = await createNewRow(rowData, parentId);
                        if (newId) {
                            row.setAttribute('data-id', newId);
                            updateRowHandlers(currentRowId, newId);
                            showToast('✓ Строка сохранена', 'success');
                        }
                    } else {
                        await saveField(currentRowId, 'article', article);
                        await saveField(currentRowId, 'name', data.title);
                    }
                }
            } else {
                nameInput.placeholder = 'Артикул не найден';
                nameInput.removeAttribute('readonly');
                nameInput.style.background = '#fff3e0';
            }
        } catch (error) {
            console.error('Ошибка:', error);
        } finally {
            articleInput.classList.remove('loading');
            updateStats();
        }
    }, 1000);
};

// ========== СОХРАНЕНИЕ ПОЛЕЙ ==========

window.autoSaveLocation = async function(select, rowId) {
    if (!rowId.toString().startsWith('new_')) {
        await saveField(rowId, 'location', select.value);
        showToast('✓ Место сохранено', 'success');
    }
};

window.autoSaveQuantity = async function(input, rowId) {
    if (!rowId.toString().startsWith('new_')) {
        await saveField(rowId, 'quantity', input.value);
        updateStats();
    }
};

window.autoSaveComment = async function(input, rowId) {
    if (!rowId.toString().startsWith('new_')) {
        await saveField(rowId, 'comment', input.value);
    }
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
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
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
    
    let locationOptions = '<option value="">-- Выберите место --</option>';
    locationsList.forEach(loc => { locationOptions += `<option value="${loc}">${loc}</option>`; });
    
    newRow.innerHTML = `
        <td class="expand-cell" style="text-align: center;"></td>
        <td><input type="text" class="number-input" placeholder="Введите №"></td>
        <td><input type="date" class="date-input"></td>
        <td><input type="text" class="article-input" placeholder="Введите артикул" oninput="autoFillName(this, '${newId}')"></td>
        <td><input type="text" class="name-input" readonly style="background:#f9fafb; width:100%; min-width:100px;" placeholder="Наименование"></td>
        <td><select class="location-input">${locationOptions}</select></td>
        <td><input type="number" class="quantity-input" placeholder="0"></td>
        <td><input type="text" class="comment-input" placeholder="Комментарий"></td>
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

function updateRowHandlers(oldId, newId) {
    const row = document.querySelector(`tr[data-id="${oldId}"]`);
    if (!row) return;
    row.setAttribute('data-id', newId);
    
    const articleInput = row.querySelector('.article-input');
    if (articleInput) articleInput.setAttribute('oninput', `autoFillName(this, ${newId})`);
    
    const addBtn = row.querySelector('.add-child-btn');
    const nameInput = row.querySelector('.name-input');
    if (addBtn) {
        addBtn.setAttribute('onclick', `showAddChildModal(${newId}, '${(nameInput?.value || '').replace(/'/g, "\\'")}')`);
    }
    
    const deleteBtn = row.querySelector('.delete-btn');
    if (deleteBtn) deleteBtn.setAttribute('onclick', `showDeleteModal(${newId})`);
    
    const inputs = row.querySelectorAll('input, select');
    inputs.forEach(input => {
        const fieldName = input.classList.contains('number-input') ? 'number' :
                         input.classList.contains('date-input') ? 'arrival_date' :
                         input.classList.contains('article-input') ? 'article' :
                         input.classList.contains('quantity-input') ? 'quantity' :
                         input.classList.contains('comment-input') ? 'comment' : '';
        if (fieldName) setupAutoSave(input, newId, fieldName);
    });
}

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

// ========== ФИЛЬТРАЦИЯ (ПОИСК) - ИСПРАВЛЕННАЯ ==========

window.filterTable = function() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) {
        console.error('❌ search-input не найден');
        return;
    }
    
    const searchTerm = searchInput.value.toLowerCase().trim();
    console.log(`🔍 Поиск: "${searchTerm}"`);
    
    const clearBtn = document.querySelector('.search-clear');
    if (clearBtn) {
        clearBtn.style.display = searchTerm ? 'flex' : 'none';
    }
    
    const allRows = document.querySelectorAll('#table-body > tr[data-id]');
    
    // Если поиск пустой - показываем все
    if (searchTerm === '') {
        allRows.forEach(row => row.style.display = '');
        document.querySelectorAll('.child-row').forEach(child => child.style.display = 'none');
        document.querySelectorAll('.expand-btn i').forEach(icon => {
            icon.className = 'fas fa-chevron-right';
        });
        const searchNoData = document.getElementById('search-no-data');
        if (searchNoData) searchNoData.remove();
        updateStats();
        return;
    }
    
    // Скрываем все дочерние
    document.querySelectorAll('.child-row').forEach(child => {
        child.style.display = 'none';
    });
    
    let visibleCount = 0;
    let foundIds = new Set();
    
    allRows.forEach(row => {
        // Получаем значения из всех полей
        const number = row.querySelector('.number-input')?.value || '';
        const article = row.querySelector('.article-input')?.value || '';
        const name = row.querySelector('.name-input')?.value || '';
        const location = row.querySelector('.location-input')?.value || '';
        const comment = row.querySelector('.comment-input')?.value || '';
        
        // Объединяем все поля для поиска
        const fullText = `${number} ${article} ${name} ${location} ${comment}`.toLowerCase();
        const matches = fullText.includes(searchTerm);
        
        const rowId = row.getAttribute('data-id');
        
        console.log(`  Строка ${rowId}: "${name}" -> совпадение: ${matches}`);
        
        if (matches) {
            row.style.display = '';
            visibleCount++;
            foundIds.add(rowId);
            
            // Показываем родителей
            let parentId = row.getAttribute('data-parent');
            while (parentId && parentId !== '' && parentId !== 'null') {
                const parentRow = document.querySelector(`tr[data-id="${parentId}"]`);
                if (parentRow) {
                    parentRow.style.display = '';
                    foundIds.add(parentId);
                    
                    // Раскрываем родителя
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
            // Скрываем родителя, если у него нет видимых детей
            const hasVisibleChildren = row.querySelectorAll('.child-row:not([style*="display: none"])').length > 0;
            if (!hasVisibleChildren) {
                row.style.display = 'none';
            }
        }
    });
    
    console.log(`✅ Найдено совпадений: ${visibleCount}`);
    
    // Удаляем старое сообщение
    const searchNoData = document.getElementById('search-no-data');
    if (searchNoData) searchNoData.remove();
    
    // Если ничего не найдено
    if (visibleCount === 0 && allRows.length > 0) {
        const tbody = document.getElementById('table-body');
        const emptyRow = document.createElement('tr');
        emptyRow.id = 'search-no-data';
        emptyRow.innerHTML = `
            <td colspan="9">
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>Ничего не найдено по запросу "<strong>${searchTerm}</strong>"</p>
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

// ========== ИНИЦИАЛИЗАЦИЯ ==========

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== СТРАНИЦА ЗАГРУЖЕНА ===');
    loadLocations();
    updateStats();
    
    // Настраиваем автосохранение для существующих строк
    document.querySelectorAll('#table-body > tr[data-id]').forEach(row => {
        const rowId = row.getAttribute('data-id');
        if (!rowId.toString().startsWith('new_')) {
            row.querySelectorAll('input, select').forEach(input => {
                const fieldName = input.classList.contains('number-input') ? 'number' :
                                 input.classList.contains('date-input') ? 'arrival_date' :
                                 input.classList.contains('article-input') ? 'article' :
                                 input.classList.contains('quantity-input') ? 'quantity' :
                                 input.classList.contains('comment-input') ? 'comment' : '';
                if (fieldName) setupAutoSave(input, rowId, fieldName);
            });
        }
    });
    
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
    
    console.log('Доступные команды:');
    console.log('  filterTable() - фильтрация');
    console.log('  clearSearch() - очистить поиск');
});