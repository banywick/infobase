document.addEventListener('DOMContentLoaded', function() {
    const magicButton = document.getElementById('magic_button');
    const saveForm = document.getElementById('save_comparison_form');
    const saveButton = document.getElementById('save_comparison_btn');
    const kdTitleElement = document.getElementById('kd_title');
    const positionArticle = document.getElementById('position_article_comp');
    const positionName = document.getElementById('position_name_comp');
    const successNotification = document.getElementById('successNotification');
    
    const DEFAULT_KD_MESSAGE = 'Что бы получить наименование воспользуйтесь кнопкой <<АВТОПОИСК>>';

    // Функция для показа уведомления
    function showSuccessNotification(message = 'Сопоставление успешно сохранено!') {
        if (!successNotification) return;
        
        // Обновляем сообщение если нужно
        const messageElement = successNotification.querySelector('.notification-message');
        if (messageElement) {
            messageElement.textContent = message;
        }
        
        // Убираем класс hidden и fade-out
        successNotification.classList.remove('hidden', 'fade-out');
        
        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            successNotification.classList.add('fade-out');
            setTimeout(() => {
                successNotification.classList.add('hidden');
                successNotification.classList.remove('fade-out');
            }, 500);
        }, 3000);
    }

    // Функция для очистки полей
    function clearFields() {
        // Очищаем поле поиска
        const searchInput = document.getElementById('search_input');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Сбрасываем чекбокс
        const searchByAnalogCheckbox = document.getElementById('search_by_analog');
        if (searchByAnalogCheckbox) {
            searchByAnalogCheckbox.checked = false;
        }
        
        // Очищаем kd_title и возвращаем сообщение по умолчанию
        if (kdTitleElement) {
            kdTitleElement.textContent = DEFAULT_KD_MESSAGE;
            console.log(kdTitleElement)
        }
        
        // Деактивируем кнопку сохранения
        if (saveButton) {
            saveButton.disabled = true;
        }
        
    }

    // Функция для проверки валидности kd_title
    function checkKdTitleAndEnableButton() {
        if (kdTitleElement && saveButton) {
            const currentText = kdTitleElement.textContent.trim();
            if (currentText && currentText !== DEFAULT_KD_MESSAGE) {
                saveButton.disabled = false;
                 // console.log('Кнопка сохранения активирована');
            } else {
                saveButton.disabled = true;
                 // console.log('Кнопка сохранения деактивирована');
            }
        }
    }

    // Обработчик отправки формы сохранения
    if (saveForm) {
        saveForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!positionArticle || !positionName || !kdTitleElement) {
                console.error('Не найдены необходимые элементы');
                return;
            }

            // Проверяем, что kd_title содержит реальные данные
            const kdText = kdTitleElement.textContent.trim();
            if (!kdText || kdText === DEFAULT_KD_MESSAGE) {
                alert('Сначала получите наименование КД через автопоиск');
                return;
            }

            // Получаем CSRF-токен
            const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
            
            if (!csrfToken) {
                console.error('CSRF токен не найден');
                return;
            }

            // Подготавливаем данные для отправки
            const formData = {
                accounting_code: positionArticle.textContent.trim(),
                nomenclature_kd: kdText,
                accounting_name: positionName.textContent.trim()
            };

             // console.log('Отправляемые данные:', formData);

            try {
                const response = await fetch('/finder/comparison/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify(formData),
                    credentials: 'include',
                });

                const result = await response.json();

                if (response.ok) {
                    // Показываем кастомное уведомление вместо alert
                    showSuccessNotification('✓ Сопоставление успешно сохранено!');
                     // console.log('Ответ сервера:', result);
                    
                    // Очищаем поля после успешного сохранения
                    clearFields();
                    
                } else {
                    // Для ошибок показываем alert (или тоже можно заменить на кастомное уведомление об ошибке)
                    alert(`Ошибка при сохранении: ${result.error || 'Неизвестная ошибка'}`);
                    console.error('Ошибка сервера:', result);
                }
            } catch (error) {
                alert('Ошибка при отправке запроса');
                console.error('Ошибка:', error);
            }
        });
    }

    // Обработчик магической кнопки (обновленный)
    if (magicButton) {
        magicButton.addEventListener('click', async () => {
            try {
                const clipboardText = await navigator.clipboard.readText();
                 // console.log('Исходное содержимое буфера обмена:', clipboardText);

                // Проверка длины строки
                if (clipboardText.length > 150) {
                    console.error('Ошибка: текст из буфера обмена слишком длинный. Максимум 150 символов.');
                    return;
                }

                // Получаем CSRF-токен из cookie
                const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];

                const response = await fetch('/finder/auto_find/', {
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
                 // console.log('Обработанный результат с сервера:', result.processed_text);
                
                // Вставляем результат в поле поиска
                const searchInput = document.getElementById('search_input');
                if (searchInput) {
                    searchInput.value = result.processed_text;
                } else {
                    console.error('Элемент search_input не найден');
                    return;
                }
                
                // Вставляем исходное значение из буфера в элемент kd_title
                if (kdTitleElement) {
                    kdTitleElement.textContent = clipboardText;
                     // console.log('Значение вставлено в kd_title:', clipboardText);
                    
                    // Проверяем и активируем кнопку сохранения
                    checkKdTitleAndEnableButton();
                } else {
                    console.error('Элемент kd_title не найден');
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
                
                 // console.log('Все действия выполнены успешно');

            } catch (err) {
                console.error('Ошибка:', err);
            }
        });
    }

    // Первоначальная проверка состояния кнопки
    checkKdTitleAndEnableButton();

    // Наблюдаем за изменениями в kd_title
    if (kdTitleElement) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    checkKdTitleAndEnableButton();
                }
            });
        });

        observer.observe(kdTitleElement, {
            characterData: true,
            childList: true,
            subtree: true
        });
    }
});