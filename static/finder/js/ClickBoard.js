document.addEventListener('DOMContentLoaded', function() {
    const magicButton = document.getElementById('magic_button');

    magicButton.addEventListener('click', async () => {
        try {
            const clipboardText = await navigator.clipboard.readText();
            console.log('Исходное содержимое буфера обмена:', clipboardText);

            // Проверка длины строки
            if (clipboardText.length > 60) {
                console.error('Ошибка: текст из буфера обмена слишком длинный. Максимум 60 символов.');
                return; // Прерываем выполнение
            }

            // Получаем CSRF-токен из cookie
            const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];

            const response = await fetch('http://127.0.0.1:8000/finder/auto_find/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // Передаём CSRF-токен
                },
                body: JSON.stringify({ text: clipboardText }),
                credentials: 'include',  // Важно для передачи cookie
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Обработанный результат с сервера:', result.processed_text);

        } catch (err) {
            console.error('Ошибка:', err);
        }
    });
});
