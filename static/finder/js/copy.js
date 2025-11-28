// Универсальная функция копирования для HTTP и HTTPS
async function copyToClipboard(text) {
    // Пробуем современный API (работает на HTTPS и в современных браузерах на HTTP)
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.log('Clipboard API failed, trying fallback:', err);
        }
    }
    
    // Fallback метод (работает везде)
    return fallbackCopyToClipboard(text);
}

function fallbackCopyToClipboard(text) {
    return new Promise((resolve, reject) => {
        // Создаем временный textarea элемент
        const textArea = document.createElement('textarea');
        textArea.value = text;
        
        // Стили чтобы элемент был невидимый
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = '0';
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';
        textArea.style.opacity = '0';
        textArea.style.zIndex = '-1';
        
        document.body.appendChild(textArea);
        
        try {
            // Выделяем и копируем текст
            textArea.select();
            textArea.setSelectionRange(0, 99999); // Для мобильных устройств
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                resolve(true);
            } else {
                reject(new Error('Не удалось скопировать текст'));
            }
        } catch (err) {
            document.body.removeChild(textArea);
            reject(err);
        }
    });
}

// Функция показа визуальной обратной связи
function showVisualFeedback(iconColumn) {
    const icon = iconColumn.querySelector('img');
    if (!icon) return;
    
    // Сохраняем оригинальные стили
    const originalFilter = icon.style.filter;
    const originalTransform = icon.style.transform;
    
    // Визуальный эффект
    icon.style.filter = 'brightness(1.1) sepia(1) hue-rotate(90deg) saturate(5)';
    icon.style.transform = 'scale(1.2)';
    icon.style.transition = 'all 0.3s ease-out';
    
    // Создаем и показываем подсказку
    showTooltip(iconColumn, 'Скопировано!');
    
    // Возвращаем оригинальные стили через 1 секунду
    setTimeout(() => {
        icon.style.filter = originalFilter;
        icon.style.transform = originalTransform;
    }, 1000);
}

// Функция показа всплывающей подсказки
function showTooltip(iconColumn, message) {
    // Удаляем старые подсказки если есть
    const oldTooltip = iconColumn.querySelector('.copy-tooltip');
    if (oldTooltip) {
        oldTooltip.remove();
    }
    
    const tooltip = document.createElement('div');
    tooltip.className = 'copy-tooltip';
    tooltip.textContent = message;
    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = '#4CAF50';
    tooltip.style.color = 'white';
    tooltip.style.padding = '4px 8px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.top = '-30px';
    tooltip.style.left = '50%';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.opacity = '0';
    tooltip.style.transition = 'opacity 0.3s';
    tooltip.style.zIndex = '1000';
    tooltip.style.whiteSpace = 'nowrap';
    tooltip.style.pointerEvents = 'none';
    
    iconColumn.style.position = 'relative';
    iconColumn.appendChild(tooltip);
    
    // Анимация появления
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
    
    // Автоматическое скрытие через 1.5 секунды
    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, 300);
    }, 1500);
}

// Функция показа уведомления о копировании
function showCopyFeedback(message, isSuccess) {
    // Удаляем старые уведомления
    const oldFeedback = document.querySelector('.copy-feedback');
    if (oldFeedback) {
        oldFeedback.remove();
    }
    
    const feedback = document.createElement('div');
    feedback.className = `copy-feedback ${isSuccess ? 'success' : 'error'}`;
    feedback.textContent = message;
    
    // Стили для уведомления
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        transition: all 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
        background-color: ${isSuccess ? '#4CAF50' : '#f44336'};
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(feedback);
    
    // Автоматическое скрытие
    setTimeout(() => {
        feedback.style.opacity = '0';
        feedback.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 300);
    }, 3000);
}

// Основная функция для обработки кликов по иконкам копирования
function setupCopyIconListener() {
    document.addEventListener('click', async function(event) {
        const iconColumn = event.target.closest('.copy_visual_box');
        if (!iconColumn) return;

        event.stopPropagation();
        const row = iconColumn.closest('tr');
        
        // Получаем данные из 4-го (code) и 6-го (quantity) столбцов
        const codeElement = row.querySelector('.data-column:nth-child(5)');
        const quantityElement = row.querySelector('.data-column:nth-child(6)');
        
        if (!codeElement || !quantityElement) {
            console.error('Не найдены нужные столбцы');
            return;
        }
        
        const code = codeElement.textContent.trim();
        const quantity = quantityElement.textContent.trim();

        // Создаем текст для буфера с разделением табуляцией
        const textForClipboard = `${code}\t${quantity}`;

        try {
            // Копируем в буфер обмена
            await copyToClipboard(textForClipboard);
            
            // Показываем визуальную обратную связь
            showVisualFeedback(iconColumn);
            
        } catch (error) {
            console.error('Ошибка копирования:', error);
            showCopyFeedback('Ошибка копирования: ' + error.message, false);
        }
    });
}

// Функция для копирования всех закрепленных строк
async function copyAllPinnedRows() {
    const pinnedRows = document.querySelectorAll('#pinnedRows tr');
    if (pinnedRows.length === 0) {
        showCopyFeedback('Нет закрепленных позиций для копирования', false);
        return;
    }

    let clipboardText = '';
    
    pinnedRows.forEach(row => {
        const cells = row.querySelectorAll('td.data-column');
        if (cells.length >= 6) {
            const article = cells[1]?.textContent.trim() || '';
            const title = cells[3]?.textContent.trim() || '';
            if (article && title) {
                clipboardText += `${article}\t${title}\n`;
            }
        }
    });

    if (clipboardText.trim()) {
        try {
            await copyToClipboard(clipboardText.trim());
            showCopyFeedback(`Скопировано: ${pinnedRows.length} позиций`, true);
            
            // Визуальная обратная связь для иконки
            const icon = document.querySelector('.copy_all_pin');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    icon.style.transform = 'scale(1)';
                }, 300);
            }
        } catch (error) {
            console.error('Copy error:', error);
            showCopyFeedback('Ошибка копирования', false);
        }
    } else {
        showCopyFeedback('Нет данных для копирования', false);
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    setupCopyIconListener();
    
    // Добавляем обработчик для кнопки копирования всех закрепленных
    const copyAllButton = document.querySelector('.copy_all_pin');
    if (copyAllButton) {
        copyAllButton.addEventListener('click', copyAllPinnedRows);
    }
    
    console.log('Copy functionality initialized - works on both HTTP and HTTPS');
});

// Экспорт функций для глобального использования (если нужно)
window.copyToClipboard = copyToClipboard;
window.copyAllPinnedRows = copyAllPinnedRows;
window.showCopyFeedback = showCopyFeedback;