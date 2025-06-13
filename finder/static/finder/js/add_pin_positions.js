document.addEventListener('DOMContentLoaded', function() {
    initPinnedRows();
});


function initPinnedRows() {
    fetchPinnedData();
    document.getElementById('pinnedRows').addEventListener('click', handlePinnedRowClick);
    document.getElementById('copy_all_pin').addEventListener('click', copyAllPinnedRows);
    
    // Обработчик для кнопок закрепления в основной таблице
    document.addEventListener('click', function(event) {
        const pinButton = event.target.closest('.id_positoin_row');
        if (pinButton) {
            // Добавляем визуальный эффект на кнопку
            const icon = pinButton.querySelector('img');
            if (icon) {
                icon.classList.add('pinning-effect');
                setTimeout(() => icon.classList.remove('pinning-effect'), 500);
            }
            
            // Обновляем закрепленные позиции с задержкой
            setTimeout(fetchPinnedData, 500);
        }
    });
}





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
        renderPinnedRows(data);
    })
    .catch(error => {
        console.error('Error fetching pinned data:', error);
    });
}

function renderPinnedRows(data) {
    const pinnedRows = document.getElementById('pinnedRows');
    if (!pinnedRows) return;

    if (!data || Object.keys(data).length === 0) {
        pinnedRows.innerHTML = '';
        return;
    }

    const dataArray = Object.values(data);
    const currentIds = Array.from(pinnedRows.children).map(row => row.dataset.id);
    const newIds = dataArray.map(item => item.id);

    // Удаляем строки, которых больше нет в данных
    Array.from(pinnedRows.children).forEach(row => {
        if (!newIds.includes(row.dataset.id)) {
            row.classList.add('unpinning-row');
            row.addEventListener('animationend', () => row.remove());
        }
    });

    // Добавляем новые строки с анимацией
    dataArray.forEach(item => {
        if (!currentIds.includes(item.id)) {
            const row = createPinnedRow(item);
            pinnedRows.appendChild(row);
            // Запускаем анимацию после добавления в DOM
            setTimeout(() => row.classList.add('pinned-row'), 10);
        }
    });
}

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

function handlePinnedRowClick(event) {
    // Обработка открепления
    if (event.target.closest('.unpin-button')) {
        const button = event.target.closest('.unpin-button');
        const row = button.closest('tr');
        const data_id = button.getAttribute('data-id');
        
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
                // Удаляем строку после завершения анимации
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

// Остальные функции остаются без изменений