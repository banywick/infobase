  // Полный исправленный код поп-ап менеджера
document.addEventListener('DOMContentLoaded', function() {
    // Переменные для перетаскивания
    let isDragging = false;
    let currentPopup = null;
    let offsetX = 0;
    let offsetY = 0;

    // Функция для открытия поп-апа
    function openPopup(popupId) {
        const popup = document.getElementById(popupId);
        if (!popup) return;

        // Закрываем все другие поп-апы
        document.querySelectorAll('.my-popup').forEach(p => {
            if (p !== popup) p.classList.remove('active');
        });

        // Открываем нужный поп-ап
        popup.classList.add('active');

        // Сбрасываем позицию поп-апа в центр
        const content = popup.querySelector('.popup-content');
        if (content) {
            content.style.left = '';
            content.style.top = '';
            content.style.transform = 'translate(-50%, -50%)';
        }
    }

    // Функция для закрытия поп-апа
    function closePopup(popup) {
        popup.classList.remove('active');
    }

    // Функция для начала перетаскивания
    function startDrag(e, popup) {
        const header = popup.querySelector('.popup-header');
        if (!header) return;

        if (e.target.closest('.popup-header')) {
            isDragging = true;
            currentPopup = popup;

            const content = popup.querySelector('.popup-content');
            const rect = content.getBoundingClientRect();

            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;

            header.classList.add('dragging');
            document.body.style.cursor = 'grabbing';
            e.preventDefault();
        }
    }

    // Функция для перемещения окна
    function drag(e) {
        if (!isDragging || !currentPopup) return;

        const content = currentPopup.querySelector('.popup-content');
        if (!content) return;

        let newX = e.clientX - offsetX;
        let newY = e.clientY - offsetY;

        const maxX = window.innerWidth - content.offsetWidth;
        const maxY = window.innerHeight - content.offsetHeight;

        newX = Math.max(0, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));

        content.style.left = newX + 'px';
        content.style.top = newY + 'px';
        content.style.transform = 'none';
    }

    // Функция для завершения перетаскивания
    function stopDrag() {
        if (!isDragging || !currentPopup) return;

        const header = currentPopup.querySelector('.popup-header');
        if (header) {
            header.classList.remove('dragging');
            header.style.cursor = 'move';
        }

        document.body.style.cursor = '';
        isDragging = false;
        currentPopup = null;
        offsetX = 0;
        offsetY = 0;
    }

    // Делегирование событий для открытия поп-апов
    document.addEventListener('click', function(e) {
        // Открытие поп-апа по клику на кнопку
        if (e.target.classList.contains('open-btn')) {
            const popupId = e.target.getAttribute('data-popup');
            openPopup(popupId);
        }

        // Закрытие поп-апа по клику на крестик
        if (e.target.classList.contains('close-btn')) {
            const popup = e.target.closest('.my-popup');
            if (popup) closePopup(popup);
        }
    });

    // Закрытие поп-апа по клику вне окна
    document.querySelectorAll('.my-popup').forEach(popup => {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                closePopup(popup);
            }
        });
    });

    // Закрытие поп-апа по клавише ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activePopup = document.querySelector('.my-popup.active');
            if (activePopup) closePopup(activePopup);
        }
    });

    // Обработчики перетаскивания
    document.addEventListener('mousedown', function(e) {
        const activePopup = document.querySelector('.my-popup.active');
        if (activePopup && activePopup.contains(e.target)) {
            startDrag(e, activePopup);
        }
    });

    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    });
