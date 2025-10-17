// Глобальные переменные для управления пагинацией
let selectedProject = null;
let isLoading = false;
let currentPage = 1;
const ITEMS_PER_PAGE = 100; // Фиксированное количество элементов на страницу
let hasMoreData = true;
let abortController = null;

// Обработчик клика на элементы проектов
document.addEventListener('click', function(e) {
    const projectContent = e.target.closest('.project-content');
    if (projectContent) {
        const projectSpan = projectContent.querySelector('span');
        if (projectSpan) {
            selectedProject = projectSpan.textContent.trim();
            
            // Сброс пагинации при выборе нового проекта
            resetPagination();
            
            // Визуальное выделение
            document.querySelectorAll('.project-content').forEach(el => {
                el.classList.remove('selected');
            });
            projectContent.classList.add('selected');
        }
    }
});

// Обработчик клика на кнопку фильтра
document.getElementById('button_filter_view_all').addEventListener('click', function() {
    const popup = document.getElementById('choice_project_popup');
    
    if (!selectedProject) {
        alert('Пожалуйста, выберите проект');
        return;
    }
    
    // Сброс и начальная загрузка
    resetPagination();
    loadMoreData(true);
    
    // Закрываем popup
    if (popup) popup.style.display = 'none';
});

// Сброс состояния пагинации
function resetPagination() {
    currentPage = 1;
    hasMoreData = true;
    const tbody = document.querySelector('tbody:not(.pinned-block)');
    if (tbody) tbody.innerHTML = '';
    document.querySelector('.not_found').style.display = 'none';
    document.getElementById('loadMoreBtn').style.display = 'none';
    
    // Отмена предыдущего запроса
    if (abortController) {
        abortController.abort();
    }
}

// Основная функция загрузки данных
async function loadMoreData(isInitialLoad = false) {
    if (isLoading || !hasMoreData) return;
    
    isLoading = true;
    const tbody = document.querySelector('tbody:not(.pinned-block)');
    const notFound = document.querySelector('.not_found');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    try {
        // Создаем новый AbortController
        abortController = new AbortController();
        
        // Показываем индикатор загрузки
        showLoadingIndicator(tbody, isInitialLoad);
        
        const response = await fetch('/finder/all_products_filter_project/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 
                project_name: selectedProject,
                page: currentPage
            }),
            signal: abortController.signal
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        
        // Удаляем индикатор загрузки
        removeLoadingIndicator(tbody);
        
        // Обработка полученных данных
        if (data.results && data.results.length > 0) {
            renderTableData(data.results, tbody, notFound, isInitialLoad);
            hasMoreData = data.next !== null;
            currentPage++;
            
            // Показываем кнопку "Показать еще" если есть еще данные
            loadMoreBtn.style.display = hasMoreData ? 'block' : 'none';
        } else if (isInitialLoad) {
            // Нет данных для первой загрузки
            notFound.style.display = 'block';
            hasMoreData = false;
            loadMoreBtn.style.display = 'none';
        } else {
            // Нет больше данных для подгрузки
            hasMoreData = false;
            loadMoreBtn.style.display = 'none';
        }
        
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Запрос был прерван');
            return;
        }
        
        console.error('Ошибка загрузки:', error);
        showErrorIndicator(tbody, isInitialLoad);
        loadMoreBtn.style.display = 'none';
    } finally {
        isLoading = false;
    }
}

// Функции для работы с UI
function showLoadingIndicator(tbody, isInitialLoad) {
    if (!tbody) return;
    
    if (isInitialLoad) {
        tbody.innerHTML = '<tr><td colspan="12" class="loading">Загрузка данных...</td></tr>';
    } else {
        const loadingRow = document.createElement('tr');
        loadingRow.innerHTML = '<td colspan="12" class="loading">Загрузка дополнительных данных...</td>';
        tbody.appendChild(loadingRow);
    }
}

function removeLoadingIndicator(tbody) {
    if (!tbody) return;
    const loadingRows = tbody.querySelectorAll('tr .loading');
    loadingRows.forEach(row => row.closest('tr').remove());
}

function showErrorIndicator(tbody, isInitialLoad) {
    if (!tbody) return;
    
    if (isInitialLoad) {
        tbody.innerHTML = '<tr><td colspan="12" class="error">Ошибка загрузки данных</td></tr>';
    } else {
        const errorRow = document.createElement('tr');
        errorRow.innerHTML = '<td colspan="12" class="error">Ошибка загрузки</td>';
        tbody.appendChild(errorRow);
    }
}

// Функция рендеринга данных таблицы
function renderTableData(data, tbody, notFound, clearTable = true) {
    if (!tbody) return;
    
    if (clearTable) {
        tbody.innerHTML = '';
    }
    
    if (!data || data.length === 0) {
        if (clearTable) {
            notFound.style.display = 'block';
        }
        return;
    }
    
    notFound.style.display = 'none';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.classList.add('table-row');
        
        row.innerHTML = `
            <td class="icon-column">
                <button class="id_positoin_row" data-id="${item.id}">
                    <img id="keep_icon" src="${staticUrls?.keepIcon || ''}" alt="Закрепить" title="Закрепить позицию">
                </button>
            </td>
            <td class="icon-column">
            ${item.notes_part ? `
                <img src="${staticUrls?.commentIcon || ''}" 
                    alt="Комментарий" 
                    class="notes-icon" 
                    title="${item.notes_part}">
            ` : ''}
            </td>
            <td class="data-column">${escapeHtml(item.party || '')}</td>
            <td class="data-column">${escapeHtml(item.article || '')}</td>
            <td class="data-column">${escapeHtml(item.code || '')}</td>
            <td class="data-column">${escapeHtml(item.title || '')}</td>
            <td class="icon-column">
            <div class="copy_visual_box">
                    <img src="${staticUrls?.copyIcon || ''}" alt="Копировать" class="copy-icon" title="Копировать артикул и наименование">
            </div>        
            </td>
            <td class="data-column">${escapeHtml(item.quantity || '')}</td>
            <td class="data-column">${escapeHtml(item.base_unit || '')}</td>
            <td class="data-column">${escapeHtml(item.price || '')}</td>
            <td class="icon-column">
                <div class="circle_table" style="
                    background-color: ${item.status_color || '#ccc'};
                    width: 10px;
                    height: 10px;
                    border-radius: 100%"
                    title="Статус">
                </div>
            </td>
            <td class="data-column">${escapeHtml(item.project || '')}</td>
            <td class="data-column">${escapeHtml(item.comment || '')}</td>
        `;
        
        tbody.appendChild(row);
    });
    

    function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

    // Обработчик для кнопок закрепления
    tbody.addEventListener('click', function(event) {
        if (event.target.closest('.id_positoin_row')) {
            const button = event.target.closest('.id_positoin_row');
            const data_id = button.getAttribute('data-id');
            
            fetch(`/finder/add_fix_positions_to_session/${data_id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => response.json())
            .then(data => {
                button.closest('tr')?.remove();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
}

// Инициализация кнопки "Показать еще"
function initLoadMoreButton() {
    const loadMoreBtn = document.createElement('button');
    loadMoreBtn.id = 'loadMoreBtn';
    loadMoreBtn.textContent = 'Показать еще';
    loadMoreBtn.style.display = 'none';
    loadMoreBtn.style.margin = '20px auto';
    loadMoreBtn.style.padding = '10px 20px';
    loadMoreBtn.style.backgroundColor = '#4CAF50';
    loadMoreBtn.style.color = 'white';
    loadMoreBtn.style.border = 'none';
    loadMoreBtn.style.borderRadius = '4px';
    loadMoreBtn.style.cursor = 'pointer';
    
    loadMoreBtn.addEventListener('click', function() {
        loadMoreData();
    });
    
    document.querySelector('.table-container').appendChild(loadMoreBtn);
}

// Функция для получения CSRF токена
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) return cookieValue;
    }
    return null;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initLoadMoreButton();
    
    // Удаляем обработчик скролла, так как теперь используем кнопку
    window.removeEventListener('scroll', scrollHandler);
});