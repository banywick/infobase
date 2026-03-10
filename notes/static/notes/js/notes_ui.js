// UI логика приложения заметок - ОБНОВЛЁННАЯ ВЕРСИЯ

document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const elements = {
        notesList: document.getElementById('notes-list'),
        emptyNotes: document.getElementById('empty-notes'),
        notePopup: document.getElementById('note-popup'),
        noteForm: document.getElementById('note-form'),
        noteText: document.getElementById('note-text'),
        charCount: document.getElementById('char-count'),
        popupTitle: document.getElementById('popup-title'),
        noteId: document.getElementById('note-id'),
        addNoteBtn: document.getElementById('add-note-btn'),
        addFirstNoteBtn: document.getElementById('add-first-note'),
        closePopupBtn: document.getElementById('close-popup'),
        cancelBtn: document.getElementById('cancel-btn'),
        saveBtn: document.getElementById('save-btn'),
        saveBtnText: document.getElementById('save-btn-text'),
        saveBtnSpinner: document.getElementById('save-btn-spinner'),
        notificationContainer: document.getElementById('notification-container')
    };

    // Состояние приложения
    const state = {
        currentMode: 'add', // 'add' или 'edit'
        currentNoteId: null,
        notes: []
    };

    // Инициализация приложения
    function init() {
        loadNotes();
        setupEventListeners();
        setupCharacterCounter();
    }

    // Загрузка заметок
    async function loadNotes() {
        try {
            showLoading();
            const notes = await window.NotesAPI.getAllNotes();
            state.notes = notes;
            renderNotes();
            updateNotesCount();
            updateEmptyState();
        } catch (error) {
            console.error('Ошибка при загрузке заметок:', error);
            showNotification('Ошибка при загрузке заметок', 'error');
        }
    }

    // Рендеринг списка заметок - ОБНОВЛЁННЫЙ ВАРИАНТ
    function renderNotes() {
        if (!state.notes.length) {
            elements.notesList.innerHTML = '';
            return;
        }

        elements.notesList.innerHTML = state.notes.map((note, index) => {
            const noteText = note.text || '';
            const hasScrollableContent = noteText.length > 200;
            
            return `
                <div class="note-card" data-note-id="${note.id}" style="animation-delay: ${index * 0.1}s">
                    <div class="note-header">
                        <div class="note-content-wrapper ${hasScrollableContent ? 'scrollable' : ''}">
                            <div class="note-content">
                                ${escapeHTML(noteText)}
                            </div>
                        </div>
                        <div class="note-actions">
                            <button class="btn-action btn-copy" data-note-id="${note.id}" title="Скопировать текст">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                </svg>
                            </button>
                            <button class="btn-action btn-edit" data-note-id="${note.id}" title="Редактировать">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                </svg>
                            </button>
                            <button class="btn-action btn-delete" data-note-id="${note.id}" title="Удалить">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Инициализируем обработчики событий
        initNoteEventHandlers();
    }

    // Функция для экранирования HTML
    function escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Инициализация обработчиков событий для заметок
    function initNoteEventHandlers() {
        // Обработчики для кнопок копирования
        document.querySelectorAll('.btn-copy').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const noteId = this.dataset.noteId;
                if (noteId) {
                    copyNoteText(parseInt(noteId));
                }
            });
        });
        
        // Обработчики для кнопок редактирования
        document.querySelectorAll('.btn-edit').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const noteId = this.dataset.noteId;
                if (noteId) {
                    editNote(parseInt(noteId));
                }
            });
        });
        
        // Обработчики для кнопок удаления
        document.querySelectorAll('.btn-delete').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const noteId = this.dataset.noteId;
                if (noteId) {
                    deleteNote(parseInt(noteId));
                }
            });
        });
    }

    // Копирование текста заметки
    function copyNoteText(noteId) {
        const note = state.notes.find(n => n.id === noteId);
        if (!note || !note.text) return;
        
        const text = note.text;
        
        // Используем современный Clipboard API
        navigator.clipboard.writeText(text)
            .then(() => {
                // Показать визуальную обратную связь
                const button = document.querySelector(`.btn-copy[data-note-id="${noteId}"]`);
                if (button) {
                    const originalHTML = button.innerHTML;
                    button.innerHTML = `
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"/>
                        </svg>
                    `;
                    button.classList.add('copied');
                    button.title = "Скопировано!";
                    
                    // Вернуть оригинальную иконку через 2 секунды
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                        button.classList.remove('copied');
                        button.title = "Скопировать текст";
                    }, 2000);
                }
                
                showNotification('Текст заметки скопирован в буфер обмена', 'success');
            })
            .catch(err => {
                console.error('Ошибка копирования:', err);
                showNotification('Не удалось скопировать текст', 'error');
            });
    }

    // Показать состояние загрузки
    function showLoading() {
        elements.notesList.innerHTML = `
            <div class="notes-loading">
                <div class="loading-spinner"></div>
                <p>Загружаем заметки...</p>
            </div>
        `;
    }

    // Обновить состояние пустого списка
    function updateEmptyState() {
        if (state.notes.length === 0) {
            elements.notesList.style.display = 'none';
            elements.emptyNotes.style.display = 'block';
        } else {
            elements.notesList.style.display = 'grid';
            elements.emptyNotes.style.display = 'none';
        }
    }

    // Обновить счетчик заметок
    function updateNotesCount() {
        const countElement = document.getElementById('notes-count');
        const notesCount = state.notes.length;
        
        if (countElement) {
            countElement.textContent = notesCount;
            countElement.classList.add('pulse');
            setTimeout(() => {
                countElement.classList.remove('pulse');
            }, 300);
        }
        
        // ✅ Ключевое изменение: Сохраняем количество в localStorage
        localStorage.setItem('notesCount', notesCount);
        
        // Также можно сохранять время обновления
        localStorage.setItem('notesCountUpdated', new Date().toISOString());
    }

    // Редактировать заметку
    function editNote(noteId) {
        const note = state.notes.find(n => n.id === noteId);
        if (note) {
            openPopup('edit', note);
        }
    }

    // Удалить заметку
    async function deleteNote(noteId) {
        if (!confirm('Вы уверены, что хотите удалить эту заметку?')) {
            return;
        }
        
        try {
            await window.NotesAPI.deleteNote(noteId);
            showNotification('Заметка удалена', 'success');
            await loadNotes();
        } catch (error) {
            console.error('Ошибка при удалении заметки:', error);
            showNotification('Ошибка при удалении заметки', 'error');
        }
    }

    // Открыть попап для добавления/редактирования
    function openPopup(mode = 'add', noteData = null) {
        state.currentMode = mode;
        
        if (mode === 'add') {
            elements.popupTitle.textContent = 'Добавить заметку';
            elements.noteId.value = '';
            elements.noteText.value = '';
            elements.saveBtnText.textContent = 'Добавить';
            elements.saveBtn.disabled = false;
        } else if (mode === 'edit' && noteData) {
            elements.popupTitle.textContent = 'Редактировать заметку';
            elements.noteId.value = noteData.id;
            elements.noteText.value = noteData.text || '';
            elements.saveBtnText.textContent = 'Сохранить';
            elements.saveBtn.disabled = false;
        }
        
        updateCharacterCount();
        elements.notePopup.style.display = 'block';
        setTimeout(() => {
            elements.notePopup.classList.add('active');
            elements.noteText.focus();
        }, 10);
        
        document.body.style.overflow = 'hidden';
    }

    // Закрыть попап
    function closePopup() {
        elements.notePopup.classList.add('closing');
        setTimeout(() => {
            elements.notePopup.classList.remove('active', 'closing');
            elements.notePopup.style.display = 'none';
            elements.noteForm.reset();
            state.currentNoteId = null;
            document.body.style.overflow = '';
        }, 200);
    }

    // Настройка счетчика символов
    function setupCharacterCounter() {
        elements.noteText.addEventListener('input', updateCharacterCount);
    }

    function updateCharacterCount() {
        const count = elements.noteText.value.length;
        elements.charCount.textContent = count;
        
        const counter = elements.charCount.parentElement;
        counter.classList.remove('warning', 'error');
        
        if (count > 1000) {
            counter.classList.add('error');
            elements.saveBtn.disabled = true;
        } else if (count > 800) {
            counter.classList.add('warning');
            elements.saveBtn.disabled = false;
        } else {
            elements.saveBtn.disabled = false;
        }
    }

    // Настройка обработчиков событий
    function setupEventListeners() {
        // Открытие попапа для добавления
        if (elements.addNoteBtn) {
            elements.addNoteBtn.addEventListener('click', () => openPopup('add'));
        }
        
        if (elements.addFirstNoteBtn) {
            elements.addFirstNoteBtn.addEventListener('click', () => openPopup('add'));
        }
        
        // Закрытие попапа
        if (elements.closePopupBtn) {
            elements.closePopupBtn.addEventListener('click', closePopup);
        }
        
        if (elements.cancelBtn) {
            elements.cancelBtn.addEventListener('click', closePopup);
        }
        
        // Закрытие по клику на оверлей
        if (elements.notePopup) {
            elements.notePopup.querySelector('.popup-overlay').addEventListener('click', closePopup);
        }
        
        // Обработка формы
        if (elements.noteForm) {
            elements.noteForm.addEventListener('submit', handleFormSubmit);
        }
        
        // Закрытие по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.notePopup.classList.contains('active')) {
                closePopup();
            }
        });
    }

    // Обработка отправки формы
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const text = elements.noteText.value.trim();
        const noteId = elements.noteId.value;
        
        // Валидация
        if (!text) {
            showNotification('Пожалуйста, введите текст заметки', 'error');
            elements.noteText.focus();
            return;
        }
        
        if (text.length > 1000) {
            showNotification('Заметка не должна превышать 1000 символов', 'error');
            return;
        }
        
        // Показать индикатор загрузки
        elements.saveBtn.disabled = true;
        elements.saveBtnText.style.display = 'none';
        elements.saveBtnSpinner.style.display = 'block';
        
        try {
            let result;
            
            if (state.currentMode === 'add') {
                result = await window.NotesAPI.createNote(text);
                showNotification('Заметка успешно добавлена!', 'success');
            } else if (state.currentMode === 'edit') {
                result = await window.NotesAPI.updateNote(noteId, text);
                showNotification('Заметка успешно обновлена!', 'success');
            }
            
            closePopup();
            await loadNotes();
            
        } catch (error) {
            console.error('Ошибка при сохранении заметки:', error);
            showNotification(error.message || 'Произошла ошибка при сохранении', 'error');
        } finally {
            // Скрыть индикатор загрузки
            elements.saveBtn.disabled = false;
            elements.saveBtnText.style.display = 'block';
            elements.saveBtnSpinner.style.display = 'none';
        }
    }

    // Показать уведомление
    function showNotification(message, type = 'success') {
        const container = elements.notificationContainer;
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <span class="notification-close">&times;</span>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Закрытие по клику
        notification.querySelector('.notification-close').addEventListener('click', () => {
            closeNotification(notification);
        });
        
        // Автоматическое закрытие
        setTimeout(() => {
            if (notification.parentNode) {
                closeNotification(notification);
            }
        }, 3000);
    }

    // Закрыть уведомление
    function closeNotification(notification) {
        notification.classList.remove('show');
        notification.classList.add('hide');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }

    // Запуск приложения
    init();
});