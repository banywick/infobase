// API взаимодействие с бэкендом

class NotesAPI {
    constructor() {
        this.baseUrl = '/notes';
        this.csrfToken = window.csrfToken;
        this.userId = window.currentUserId;
    }

    // Получить все заметки пользователя
    async getAllNotes() {
        try {
             // console.log('Загружаем заметки...');
            const response = await fetch(`${this.baseUrl}/all_notes/`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
             // console.log('Заметки загружены:', data);
            return data;
        } catch (error) {
            console.error('Error fetching notes:', error);
            throw error;
        }
    }

    // Создать новую заметку
    async createNote(text) {
        try {
             // console.log('Создаем заметку:', text);
            const response = await fetch(`${this.baseUrl}/add_note/`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    text: text,
                    user: this.userId
                }),
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Ошибка ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating note:', error);
            throw error;
        }
    }

    // Обновить заметку
    async updateNote(noteId, text) {
        try {
             // console.log('Обновляем заметку:', noteId, text);
            const response = await fetch(`${this.baseUrl}/edit_note/${noteId}/`, {
                method: 'PUT',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    text: text,
                    user: this.userId
                }),
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Ошибка ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating note:', error);
            throw error;
        }
    }

    // Удалить заметку
    async deleteNote(noteId) {
        try {
             // console.log('Удаляем заметку:', noteId);
            const response = await fetch(`${this.baseUrl}/remove_note/${noteId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error deleting note:', error);
            throw error;
        }
    }

    // Форматирование даты
    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Дата неизвестна';
            }
            
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) {
                return 'Сегодня';
            } else if (diffDays === 1) {
                return 'Вчера';
            } else if (diffDays < 7) {
                return `${diffDays} дня назад`;
            } else {
                return date.toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });
            }
        } catch (error) {
            console.error('Error formatting date:', error);
            return 'Дата неизвестна';
        }
    }
}

// Экспорт глобального экземпляра
window.NotesAPI = new NotesAPI();