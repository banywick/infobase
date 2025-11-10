let pinnedOrder = JSON.parse(sessionStorage.getItem('pinnedPositionsOrder')) || [];

function fetchPinnedData() {
    fetch('/finder/get_fixed_positions/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        const orderedData = getOrderedPinnedData(data);
        renderPinnedRows(orderedData);
    })
    .catch(error => {
        console.error('Error fetching pinned data:', error);
    });
}

function getOrderedPinnedData(data) {
    if (!data || typeof data !== 'object') return [];
    
    // data имеет структуру: {'19': {данные позиции}, '25': {данные позиции}, ...}
    const allIds = Object.keys(data);
    
    // Обновляем порядок: сохраняем существующий порядок, добавляем новые в конец
    const newOrder = pinnedOrder.filter(id => allIds.includes(id));
    allIds.forEach(id => {
        if (!newOrder.includes(id)) {
            newOrder.push(id);
        }
    });
    
    // Сохраняем обновленный порядок
    pinnedOrder = newOrder;
    sessionStorage.setItem('pinnedPositionsOrder', JSON.stringify(pinnedOrder));
    
    // Создаем упорядоченный массив данных
    const orderedData = [];
    pinnedOrder.forEach(positionId => {
        if (data[positionId]) {
            orderedData.push({
                id: positionId,
                ...data[positionId]
            });
        }
    });
    
    return orderedData;
}

function renderPinnedRows(data) {
    const pinnedRows = document.getElementById('pinnedRows');
    if (!pinnedRows) return;

    if (!data || data.length === 0) {
        pinnedRows.innerHTML = '';
        pinnedOrder = [];
        sessionStorage.removeItem('pinnedPositionsOrder');
        return;
    }

    // Полностью перерисовываем в правильном порядке
    pinnedRows.innerHTML = '';
    
    data.forEach(item => {
        const row = createPinnedRow(item);
        pinnedRows.appendChild(row);
        setTimeout(() => row.classList.add('pinned-row'), 10);
    });
}

// Обновляем createPinnedRow для работы с новой структурой
function createPinnedRow(item) {
    const row = document.createElement('tr');
    row.dataset.id = item.id;
    
    row.innerHTML = `
        <td class="icon-column">
        <button class="unpin-button" id="id_positoin_row" data-id="${item.id}" title="Открепить позицию">
            <img id="unpin_icon" 
                src="${staticUrls?.keepIcon || ''}" 
                alt="Открепить"
                style="filter: brightness(0) saturate(100%) invert(27%) sepia(91%) saturate(2476%) hue-rotate(346deg) brightness(104%) contrast(97%); 
                        transform: rotate(-88deg);
                        width: 24px;
                        height: 24px;">
        </button>
        </td>
        <td class="icon-column">
            ${item.notes_part ? `
                <img src="${staticUrls?.commentIcon || ''}" 
                    alt="Комментарий" 
                    class="notes-icon" 
                    title="${escapeHtml(item.notes_part)}">
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
    
    return row;
}

// Обновляем обработчик открепления
function handlePinnedRowClick(event) {
    // Обработка открепления
    if (event.target.closest('.unpin-button')) {
        const button = event.target.closest('.unpin-button');
        const row = button.closest('tr');
        const data_id = button.getAttribute('data-id');
        
        // Удаляем из порядка
        pinnedOrder = pinnedOrder.filter(id => id !== data_id);
        sessionStorage.setItem('pinnedPositionsOrder', JSON.stringify(pinnedOrder));
        
        // Анимация перед удалением
        row.classList.add('unpinning-row');
        
        // Отправка запроса после начала анимации
        setTimeout(() => {
            fetch(`/finder/remove_fix_positions_to_session/${data_id}/`, {
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
                row.addEventListener('animationend', () => row.remove());
            })
            .catch(error => {
                console.error('Error:', error);
                row.classList.remove('unpinning-row');
                alert('Ошибка при откреплении позиции');
            });
        }, 100);
        return;
    }
    
    // Обработка копирования
    if (event.target.closest('.copy-icon')) {
        handleCopyClick(event);
        return;
    }
}

// Обновляем initPinnedRows
function initPinnedRows() {
    pinnedOrder = JSON.parse(sessionStorage.getItem('pinnedPositionsOrder')) || [];
    fetchPinnedData();
    document.getElementById('pinnedRows').addEventListener('click', handlePinnedRowClick);
    document.getElementById('copy_all_pin').addEventListener('click', copyAllPinnedRows);
    
    document.addEventListener('click', function(event) {
        const pinButton = event.target.closest('.id_positoin_row');
        if (pinButton) {
            const data_id = pinButton.getAttribute('data-id');
            
            // Добавляем новую позицию в порядок (если ее еще нет)
            if (!pinnedOrder.includes(data_id)) {
                pinnedOrder.push(data_id);
                sessionStorage.setItem('pinnedPositionsOrder', JSON.stringify(pinnedOrder));
            }
            
            const icon = pinButton.querySelector('img');
            if (icon) {
                icon.classList.add('pinning-effect');
                setTimeout(() => icon.classList.remove('pinning-effect'), 500);
            }
            
            setTimeout(fetchPinnedData, 500);
        }
    });
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    initPinnedRows();
});