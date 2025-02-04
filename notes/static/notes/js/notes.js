document.getElementById('addNoteButton').addEventListener('click', function() {
    document.getElementById('noteForm').classList.toggle('hidden');
});

document.getElementById('saveNoteButton').addEventListener('click', function() {
    const noteText = document.getElementById('noteText').value;
    const formData = new FormData();
    formData.append('note', noteText);

    fetch('https://example.com/api/notes', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Заметка сохранена:', data);
        // Здесь можно добавить логику для обновления UI после сохранения заметки
    })
    .catch(error => {
        console.error('Ошибка при сохранении заметки:', error);
    });
});

document.getElementById('editNoteButton').addEventListener('click', function() {
    const noteText = document.getElementById('noteText').value;
    // Здесь вы можете вызвать ваш REST API для редактирования заметки
    console.log('Редактировать заметку:', noteText);
});

document.getElementById('deleteNoteButton').addEventListener('click', function() {
    const noteText = document.getElementById('noteText').value;
    // Здесь вы можете вызвать ваш REST API для удаления заметки
    console.log('Удалить заметку:', noteText);
});
