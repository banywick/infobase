document.addEventListener('DOMContentLoaded', function() {
    const magicButton = document.getElementById('magic_button');

    magicButton.addEventListener('click', async () => {
        try {
            const clipboardText = await navigator.clipboard.readText();
            console.log('Исходное содержимое буфера обмена:', clipboardText);

            // Проверка длины строки
            if (clipboardText.length > 150) {
                console.error('Ошибка: текст из буфера обмена слишком длинный. Максимум 150 символов.');
                return; // Прерываем выполнение
            }

            // Получаем CSRF-токен из cookie
            const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];

            const response = await fetch('http://127.0.0.1:8000/finder/auto_find/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ text: clipboardText }),
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Обработанный результат с сервера:', result.processed_text);
            
            // Вставляем результат в поле поиска
            const searchInput = document.getElementById('search_input');
            if (searchInput) {
                searchInput.value = result.processed_text;
            } else {
                console.error('Элемент search_input не найден');
                return;
            }
            
            // Активируем чекбокс search_by_analog
            const searchByAnalogCheckbox = document.getElementById('search_by_analog');
            if (searchByAnalogCheckbox) {
                searchByAnalogCheckbox.checked = true;
            } else {
                console.error('Элемент search_by_analog не найден');
                return;
            }
            
            // Нажимаем на кнопку search_icon
            const searchIcon = document.getElementById('search_icon');
            if (searchIcon) {
                searchIcon.click();
            } else {
                console.error('Элемент search_icon не найден');
                return;
            }
            
            console.log('Все действия выполнены успешно');

        } catch (err) {
            console.error('Ошибка:', err);
        }
    });
});