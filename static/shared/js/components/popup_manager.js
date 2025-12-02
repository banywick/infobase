// Ждем загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    
    // Переменные для перетаскивания
    let isDragging = false;
    let currentPopup = null;
    let offsetX = 0;
    let offsetY = 0;
    
    // 1. Находим ВСЕ окна на странице
    const allPopups = document.querySelectorAll('.my-popup');
    
    // 2. Находим ВСЕ кнопки для открытия окон
    const openButtons = document.querySelectorAll('.open-btn');
    
    // 3. Функция для начала перетаскивания
    function startDrag(e, popup) {
        const content = popup.querySelector('.popup-content');
        const header = popup.querySelector('.popup-header');
        
        // Начинаем перетаскивание только если кликнули на заголовок
        if (e.target.closest('.popup-header')) {
            isDragging = true;
            currentPopup = popup;
            
            // Получаем позицию окна
            const rect = content.getBoundingClientRect();
            
            // Запоминаем смещение мыши относительно угла окна
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            
            // Меняем стиль заголовка
            header.classList.add('dragging');
            
            // Меняем курсор
            document.body.style.cursor = 'grabbing';
            
            // Отменяем стандартное поведение
            e.preventDefault();
        }
    }
    
    // 4. Функция для перемещения окна
    function drag(e) {
        if (!isDragging || !currentPopup) return;
        
        const content = currentPopup.querySelector('.popup-content');
        const header = currentPopup.querySelector('.popup-header');
        
        // Вычисляем новую позицию окна
        let newX = e.clientX - offsetX;
        let newY = e.clientY - offsetY;
        
        // Границы экрана (чтобы окно не выходило за пределы)
        const maxX = window.innerWidth - content.offsetWidth;
        const maxY = window.innerHeight - content.offsetHeight;
        
        // Ограничиваем позицию окна
        newX = Math.max(0, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));
        
        // Применяем новую позицию
        content.style.left = newX + 'px';
        content.style.top = newY + 'px';
        
        // Убираем transform (чтобы не мешал центрированию)
        content.style.transform = 'none';
        
        // Меняем курсор
        if (header) {
            header.style.cursor = 'grabbing';
        }
    }
    
    // 5. Функция для завершения перетаскивания
    function stopDrag() {
        if (isDragging && currentPopup) {
            const header = currentPopup.querySelector('.popup-header');
            
            // Возвращаем обычные стили
            if (header) {
                header.classList.remove('dragging');
                header.style.cursor = 'move';
            }
            
            // Возвращаем курсор
            document.body.style.cursor = '';
        }
        
        // Сбрасываем состояние
        isDragging = false;
        currentPopup = null;
        offsetX = 0;
        offsetY = 0;
    }
    
    // 6. Назначаем обработчики перетаскивания для документа
    document.addEventListener('mousedown', function(e) {
        // Находим активное окно под курсором
        const activePopup = Array.from(allPopups).find(popup => 
            popup.classList.contains('active') && 
            popup.contains(e.target)
        );
        
        if (activePopup) {
            startDrag(e, activePopup);
        }
    });
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    
    // 7. Для каждого окна добавляем обработчики закрытия
    allPopups.forEach(function(popup) {
        const closeBtn = popup.querySelector('.close-btn');
        const content = popup.querySelector('.popup-content');
        
        // Обработчик закрытия по кнопке
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Чтобы не началось перетаскивание
            popup.classList.remove('active');
            
            // Возвращаем окно в центр при следующем открытии
            content.style.left = '';
            content.style.top = '';
            content.style.transform = 'translate(-50%, -50%)';
        });
        
        // Закрытие по клику вне окна (на темном фоне)
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                popup.classList.remove('active');
                
                // Возвращаем окно в центр при следующем открытии
                content.style.left = '';
                content.style.top = '';
                content.style.transform = 'translate(-50%, -50%)';
            }
        });
        
        // Закрытие по клавише ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && popup.classList.contains('active')) {
                popup.classList.remove('active');
                
                // Возвращаем окно в центр при следующем открытии
                content.style.left = '';
                content.style.top = '';
                content.style.transform = 'translate(-50%, -50%)';
            }
        });
        
        // Запрещаем перетаскивание при клике на кнопку закрытия
        closeBtn.addEventListener('mousedown', function(e) {
            e.stopPropagation();
        });
    });
    
    // 8. Для каждой кнопки открытия
    openButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Получаем ID окна из data-атрибута
            const popupId = button.getAttribute('data-popup');
            
            // Находим окно по ID
            const popup = document.getElementById(popupId);
            
            // Если окно найдено - открываем его
            if (popup) {
                // Сначала закрываем все другие окна
                allPopups.forEach(p => {
                    if (p !== popup) {
                        p.classList.remove('active');
                    }
                });
                
                // Открываем нужное окно
                popup.classList.add('active');
                
                // Сбрасываем позицию окна в центр
                const content = popup.querySelector('.popup-content');
                content.style.left = '';
                content.style.top = '';
                content.style.transform = 'translate(-50%, -50%)';
            }
        });
    });
    
    // 9. Пример: добавляем обработчик для формы
    const form = document.querySelector('.simple-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Форма отправлена!');
            
            // Находим родительское окно и закрываем его
            const popup = this.closest('.my-popup');
            if (popup) {
                popup.classList.remove('active');
            }
        });
    }
    
    // 10. Пример: добавляем кастомный контент в третье окно
    const customContent = document.getElementById('custom-content');
    if (customContent) {
        // Можно добавить любую форму или контент
        // Например, добавим кнопку для демонстрации
        const demoButton = document.createElement('button');
        demoButton.textContent = 'Демо кнопка';
        demoButton.style.cssText = `
            padding: 10px 20px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        `;
        
        demoButton.addEventListener('click', function() {
            alert('Это ваша кнопка в пустом окне!');
        });
        
        customContent.appendChild(demoButton);
    }
});