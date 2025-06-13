// Глобальные обработчики событий (добавляются один раз при загрузке страницы)
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики поиска
    document.getElementById('search_icon').addEventListener('click', handleSearch);
    document.getElementById('search_form').addEventListener('submit', handleSearch);
    
    // Общий обработчик кликов по таблице
    document.querySelector('table').addEventListener('click', handleTableClick);
});

// Объединяем логику поиска в одну функцию
function handleSearch(event) {
    event.preventDefault();
    const searchData = getFormData();
    performSearch(searchData);
}

// Функция для получения данных формы
function getFormData() {
    const form = document.getElementById('search_form');
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        // Удаляем пробелы в начале и конце строковых значений
        data[key] = typeof value === 'string' ? value.trim() : value;
    });
    
    return data;
}

// Основная функция выполнения поиска
function performSearch(searchData) {
    const tbody = document.querySelector('tbody:not(.pinned-block)');
    const not_found = document.querySelector('.not_found');
    const infoWindow = document.querySelector('.info_window');
    
    // Показываем состояние загрузки
    tbody.innerHTML = '<tr><td colspan="13" class="loading">Загрузка данных...</td></tr>';
    not_found.style.display = 'none';
    infoWindow.style.display = 'none';
    infoWindow.innerHTML = '';

    // Добавляем timestamp для избежания кэширования
    const url = `/finder/products/?t=${Date.now()}`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(searchData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Results:', data.results);
        console.log('Analogs:', data.analogs);
        console.log('Analogs_kd:', data.analogs_kd);
        
        renderInfoWindow(data, infoWindow);
        renderTableData(data.results, tbody, not_found);
    })
    .catch(error => {
        console.error('Error:', error);
        tbody.innerHTML = '<tr><td colspan="13" class="error">Ошибка загрузки данных</td></tr>';
    });
}

// Функция рендеринга информационного окна
function renderInfoWindow(data, infoWindow) {
    infoWindow.innerHTML = '';
    infoWindow.style.display = 'none';

    if (data.analogs?.length > 0) {
        renderAnalogList(infoWindow, 'Аналоги', data.analogs);
    }

    if (data.analogs_kd?.length > 0) {
        renderAnalogList(infoWindow, 'Сопоставление наименования КД \\ ТН', data.analogs_kd);
    }
}

function renderAnalogList(infoWindow, titleText, items) {
    infoWindow.style.display = 'flex';
    infoWindow.style.flexDirection = 'column';

    const title = document.createElement('h3');
    title.textContent = titleText;
    title.className = 'analogs-title';

    const listContainer = document.createElement('div');
    listContainer.className = 'analogs-container';

    items.forEach(item => {
        const analogItem = document.createElement('div');
        analogItem.className = 'analog-item';
        analogItem.textContent = item;
        listContainer.appendChild(analogItem);
    });

    infoWindow.appendChild(title);
    infoWindow.appendChild(listContainer);
}

// Функция рендеринга данных таблицы
function renderTableData(data, tbody, not_found) {
    tbody.innerHTML = '';
    
    if (!data || data.detail === "Ничего не найдено") {
        not_found.style.display = 'block';
        return;
    }
    
    not_found.style.display = 'none';
    
    if (!Array.isArray(data)) {
        console.error('Ожидался массив данных:', data);
        return;
    }

    data.forEach(item => {
        if (!item?.id) {
            console.warn('Элемент без ID:', item);
            return;
        }

        const row = document.createElement('tr');
        row.dataset.id = item.id;
        
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
        console.log(item.status_color)
    });
}

// Обработчик кликов по таблице
function handleTableClick(event) {
    // Обработка копирования
    if (event.target.closest('.copy-icon')) {
        handleCopyClick(event);
        return;
    }
    
    // Обработка закрепления
    if (event.target.closest('.id_positoin_row')) {
        handlePinClick(event);
        return;
    }
}

function handleCopyClick(event) {
    const row = event.target.closest('tr');
    if (!row) return;

    const cells = row.querySelectorAll('td.data-column');
    if (cells.length < 6) return;

    const article = cells[3].textContent; // 4-й data-column - артикул
    const title = cells[5].textContent;   // 6-й data-column - название
    
    copyToClipboard(`${article} ${title}`);
    
    // Визуальная обратная связь
    const icon = event.target.closest('.copy-icon');
    if (icon) {
        icon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            icon.style.transform = 'scale(1)';
        }, 300);
    }
}

function handlePinClick(event) {
    const button = event.target.closest('.id_positoin_row');
    if (!button) return;

    const data_id = button.getAttribute('data-id');
    if (!data_id) return;
    
    fetch(`/finder/add_fix_positions_to_session/${data_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        button.closest('tr')?.remove();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при закреплении позиции');
    });
}

// Вспомогательные функции
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Ошибка копирования:', err);
        return false;
    } finally {
        document.body.removeChild(textarea);
    }
    
    return true;
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}