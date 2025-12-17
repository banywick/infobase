// Инициализация тултипа для динамических строк
function initProjectTooltips() {
    const tooltip = document.getElementById('projectTooltip');
    
    // Используем делегирование событий для динамически созданных элементов
    document.addEventListener('mouseover', function(e) {
        const infoIcon = e.target.closest('.info_project');
        if (!infoIcon) {
            // Если курсор ушел с иконки, скрываем тултип
            if (!e.target.closest('.project-tooltip')) {
                tooltip.classList.remove('visible');
            }
            return;
        }
        
        // Получаем данные из строки
        const row = infoIcon.closest('tr');
        if (!row) return;
        
        // Собираем данные из ячеек
        const project = row.querySelector('.invoice-project')?.textContent || 'Не указан';
        const unit = row.querySelector('.invoice-unit')?.textContent || 'н/д';
        const invoiceNumber = row.querySelector('.invoice-number')?.textContent || 'н/д';
        const date = row.querySelector('.date-cell')?.textContent.trim() || 'н/д';
        const supplier = row.querySelector('.supplier-cell')?.textContent || 'н/д';
        const article = row.querySelector('.article-cell')?.textContent || 'н/д';
        const party = row.querySelector('.party-cell')?.textContent || 'н/д';
        const quantity = row.querySelector('.quantity-cell')?.textContent || 'н/д';
        const comment = row.querySelector('.comment-cell')?.textContent || '';
        const statusElement = row.querySelector('.status-cell');
        const status = statusElement?.textContent || 'н/д';
        const description = row.querySelector('.description-cell')?.textContent || '';
        const itemName = row.querySelector('td:nth-child(9)')?.textContent || ''; // Название товара
        
        // Создаем HTML для тултипа
        const tooltipHTML = `
            <h4>📋 ${project}</h4>
            <p><strong>Накладная:</strong> ${invoiceNumber}</p>
            <p><strong>Дата:</strong> ${date}</p>
            <p><strong>Поставщик:</strong> ${supplier}</p>
            <p><strong>Товар:</strong> ${itemName}</p>
            <p><strong>Артикул:</strong> ${article}</p>
            <p><strong>Партия:</strong> ${party}</p>
            <p><strong>Количество:</strong> ${quantity} ${unit}</p>
            <p><strong>Статус:</strong> ${status}</p>
            ${comment ? `<p><strong>Комментарий:</strong> ${comment}</p>` : ''}
            ${description ? `<p><strong>Описание:</strong> ${description}</p>` : ''}
        `;
        
        // Показываем тултип
        tooltip.innerHTML = tooltipHTML;
        tooltip.classList.add('visible');
        
        // Позиционируем тултип
        updateTooltipPosition(e, tooltip);
    });
    
    // Обновляем позицию при движении мыши
    document.addEventListener('mousemove', function(e) {
        const infoIcon = e.target.closest('.info_project');
        if (infoIcon && tooltip.classList.contains('visible')) {
            updateTooltipPosition(e, tooltip);
        }
    });
    
    // Скрываем тултип при уходе мыши
    document.addEventListener('mouseout', function(e) {
        const relatedTarget = e.relatedTarget;
        if (!relatedTarget || 
            (!relatedTarget.closest('.info_project') && 
             !relatedTarget.closest('.project-tooltip'))) {
            tooltip.classList.remove('visible');
        }
    });
}

// Функция обновления позиции тултипа
function updateTooltipPosition(e, tooltip) {
    const x = e.clientX + 15;
    const y = e.clientY + 15;
    
    tooltip.style.left = x + 'px';
    tooltip.style.top = (y + window.scrollY) + 'px';
    
    // Корректировка при выходе за границы
    const tooltipRect = tooltip.getBoundingClientRect();
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    // Правая граница
    if (tooltipRect.right > windowWidth) {
        tooltip.style.left = (e.clientX - tooltipRect.width - 15) + 'px';
    }
    
    // Нижняя граница
    if (tooltipRect.bottom > windowHeight) {
        tooltip.style.top = (e.clientY - tooltipRect.height - 15 + window.scrollY) + 'px';
    }
    
    // Левая граница
    if (tooltipRect.left < 0) {
        tooltip.style.left = '15px';
    }
    
    // Верхняя граница
    if (tooltipRect.top < 0) {
        tooltip.style.top = (15 + window.scrollY) + 'px';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', initProjectTooltips);

// Также инициализируем при динамическом добавлении строк
// Если у вас есть функция для добавления строк, добавьте вызов initProjectTooltips() после добавления