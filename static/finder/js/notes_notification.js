// Код для другого приложения - вставьте в его JS файл
document.addEventListener('DOMContentLoaded', function() {
    const notesCounterElement = document.querySelector('.number_count_notes');
    if (!notesCounterElement) return;
    
    // Функция обновления счетчика
    function updateNotesCounter() {
        // Получаем количество заметок из localStorage
        const notesCount = localStorage.getItem('notesCount');
        const count = notesCount ? parseInt(notesCount) : 0;
        
        if (count > 0) {
            // Показываем красный шарик с цифрой
            notesCounterElement.innerHTML = `
                <div class="notes-badge" data-count="${count}">
                    <span class="badge-count">${count}</span>
                </div>
            `;
            notesCounterElement.style.display = 'block';
        } else {
            // Скрываем шарик если заметок нет
            notesCounterElement.innerHTML = '';
            notesCounterElement.style.display = 'none';
        }
    }
    
    // Обновляем сразу при загрузке
    updateNotesCounter();
    
    // Слушаем изменения в localStorage (для обновления в реальном времени)
    window.addEventListener('storage', function(event) {
        if (event.key === 'notesCount') {
            updateNotesCounter();
        }
    });
    
    // Также можно обновлять периодически (каждые 5 секунд)
    setInterval(updateNotesCounter, 5000);
});