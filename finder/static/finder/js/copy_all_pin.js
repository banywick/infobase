// // Добавьте этот код в ваш файл (например, add_pin_positions.js)
// function setupCopyAllPinListener() {
//     const iconColumn = event.target.closest('.copy_visual_box');
//     if (!copyAllIcon) return;

//     copyAllIcon.addEventListener('click', function(event) {
//         event.stopPropagation();
        
//         const pinnedRows = document.querySelectorAll('#pinnedRows tr');
//         if (pinnedRows.length === 0) {
//             showTooltip(this, 'Нет закрепленных позиций', false);
//             return;
//         }

//         let clipboardText = '';
        
//         pinnedRows.forEach(row => {
//             const cells = row.querySelectorAll('td.data-column');
//             if (cells.length >= 6) {
//                 const article = cells[3].textContent.trim(); // 4-й столбец - артикул
//                 const title = cells[5].textContent.trim();   // 6-й столбец - название
//                 clipboardText += `${article}\t${title}\n`;
//             }
//         });

//         navigator.clipboard.writeText(clipboardText.trim())
//             .then(() => {
//                 // Применяем такую же визуализацию как в copy.js
//                 this.style.filter = 'brightness(1.1) sepia(1) hue-rotate(90deg) saturate(5)';
//                 this.style.transform = 'scale(1.2)';
//                 this.style.transition = 'all 0.3s ease-out';
                
//                 // Показываем подсказку с количеством скопированных позиций
//                 showTooltip(this, `Скопировано ${pinnedRows.length} позиций`, true);
                
//                 // Возвращаем исходный вид через 1 секунду
//                 setTimeout(() => {
//                     this.style.filter = '';
//                     this.style.transform = '';
//                 }, 1000);
//             })
//             .catch(() => {
//                 showTooltip(this, 'Ошибка копирования', false);
//             });
//     });
// }

// // Общая функция для показа подсказок (аналогичная той, что в copy.js)
// function showTooltip(element, message, isSuccess) {
//     // Удаляем старую подсказку если есть
//     const oldTooltip = element.closest('th').querySelector('.copy-tooltip');
//     if (oldTooltip) oldTooltip.remove();
    
//     // Создаем новую подсказку
//     const tooltip = document.createElement('div');
//     tooltip.className = 'copy-tooltip';
//     tooltip.textContent = message;
//     tooltip.style.position = 'absolute';
//     tooltip.style.backgroundColor = isSuccess ? '#4CAF50' : '#F44336';
//     tooltip.style.color = 'white';
//     tooltip.style.padding = '4px 8px';
//     tooltip.style.borderRadius = '4px';
//     tooltip.style.fontSize = '12px';
//     tooltip.style.top = `${element.offsetTop - 25}px`;
//     tooltip.style.left = `${element.offsetLeft + element.offsetWidth/2 - 50}px`;
//     tooltip.style.opacity = '0';
//     tooltip.style.transition = 'opacity 0.3s';
//     tooltip.style.zIndex = '1000';
//     tooltip.style.whiteSpace = 'nowrap';
    
//     // Добавляем подсказку в DOM
//     element.closest('th').style.position = 'relative';
//     element.closest('th').appendChild(tooltip);
    
//     // Показываем с небольшой задержкой
//     setTimeout(() => tooltip.style.opacity = '1', 10);
    
//     // Убираем через 1 секунду
//     setTimeout(() => {
//         tooltip.style.opacity = '0';
//         setTimeout(() => tooltip.remove(), 300);
//     }, 1000);
// }

// // Инициализация (добавьте в DOMContentLoaded или initPinnedRows)
// document.addEventListener('DOMContentLoaded', function() {
//     setupCopyAllPinListener();
//     // ... остальная инициализация
// });