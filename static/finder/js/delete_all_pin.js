// Добавляем обработчик для кнопки сброса всех закрепленных позиций
document.addEventListener('DOMContentLoaded', function() {
    const resetButton = document.getElementById('reset_all_pin');
    
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Добавляем CSS для анимации, если его еще нет
            if (!document.getElementById('remove-animation-styles')) {
                const style = document.createElement('style');
                style.id = 'remove-animation-styles';
                style.textContent = `
                    .removing-row {
                        animation: removeRow 0.3s ease-out forwards;
                    }
                    
                    @keyframes removeRow {
                        0% {
                            opacity: 1;
                            transform: translateX(0);
                        }
                        100% {
                            opacity: 0;
                            transform: translateX(30px);
                            height: 0;
                            padding: 0;
                            margin: 0;
                        }
                    }
                `;
                document.head.appendChild(style);
            }
            
            const pinnedRows = document.getElementById('pinnedRows');
            if (pinnedRows && pinnedRows.children.length > 0) {
                // Получаем все строки
                const rows = Array.from(pinnedRows.children);
                
                // Применяем анимацию к каждой строке с небольшой задержкой
                rows.forEach((row, index) => {
                    setTimeout(() => {
                        row.classList.add('removing-row');
                    }, index * 50); // Задержка 50мс между строками
                });
                
                // Очищаем таблицу после завершения анимации
                setTimeout(() => {
                    pinnedRows.innerHTML = '';
                    
                    // Очищаем sessionStorage
                    pinnedOrder = [];
                    sessionStorage.removeItem('pinnedPositionsOrder');
                    
                    // Отправляем fetch запрос на удаление из сессии
                    fetch('/finder/remove-all-fix-positions/', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Ошибка при удалении');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Все позиции удалены из сессии:', data);
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        // В случае ошибки перезагружаем данные, чтобы вернуть строки
                        fetchPinnedData();
                    });
                }, rows.length * 50 + 300); // Ждем окончания всех анимаций
                
            } else {
                // Если строк нет, просто очищаем sessionStorage и отправляем запрос
                pinnedOrder = [];
                sessionStorage.removeItem('pinnedPositionsOrder');
                
                fetch('/finder/remove-all-fix-positions/', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Все позиции удалены из сессии:', data);
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                });
            }
        });
    }
});