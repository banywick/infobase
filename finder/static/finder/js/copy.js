function setupCopyIconListener() {
    document.addEventListener('click', function(event) {
        const iconColumn = event.target.closest('.copy_visual_box');
        if (!iconColumn) return;

        event.stopPropagation();
        const row = iconColumn.closest('tr');
        
        // Получаем данные из 4-го (code) и 6-го (quantity) столбцов
        const code = row.querySelector('.data-column:nth-child(4)').textContent.trim();
        const quantity = row.querySelector('.data-column:nth-child(6)').textContent.trim();

        // Создаем текст для буфера с разделением табуляцией
        const textForClipboard = `${code}\t${quantity}`;

        // Копируем в буфер обмена
        navigator.clipboard.writeText(textForClipboard)
            .then(() => {
                const icon = iconColumn.querySelector('img');
                
                // Визуальный эффект
                icon.style.filter = 'brightness(1.1) sepia(1) hue-rotate(90deg) saturate(5)';
                icon.style.transform = 'scale(1.2)';
                icon.style.transition = 'all 0.3s ease-out';
                
                // Подсказка
                const tooltip = document.createElement('div');
                tooltip.textContent = 'Скопировано';
                tooltip.style.position = 'absolute';
                tooltip.style.backgroundColor = '#4CAF50';
                tooltip.style.color = 'white';
                tooltip.style.padding = '4px 8px';
                tooltip.style.borderRadius = '4px';
                tooltip.style.fontSize = '12px';
                tooltip.style.top = `${icon.offsetTop - 25}px`;
                tooltip.style.left = `${icon.offsetLeft + icon.offsetWidth/2 - 50}px`;
                tooltip.style.opacity = '0';
                tooltip.style.transition = 'opacity 0.3s';
                iconColumn.style.position = 'relative';
                iconColumn.appendChild(tooltip);
                
                setTimeout(() => tooltip.style.opacity = '1', 10);
                
                setTimeout(() => {
                    icon.style.filter = '';
                    icon.style.transform = '';
                    tooltip.style.opacity = '0';
                    setTimeout(() => tooltip.remove(), 300);
                }, 1000);
            })
            .catch(() => console.error('Ошибка копирования'));
    });
}

document.addEventListener('DOMContentLoaded', setupCopyIconListener);