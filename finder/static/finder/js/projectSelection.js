//Фомирование колекции при выборе проектов подсветка кнопок
// Отправка коллекции на сервер для добавления в сессию

document.addEventListener('DOMContentLoaded', function() {
// Проверяем наличие глобальной переменной staticUrls
if (typeof staticUrls === 'undefined') {
    console.error('Глобальная переменная staticUrls не определена');
    return;
}

const projectSelection = {
    selectedProjects: new Set(),
    
    init: function() {
    this.bindEvents();
    },
    
    bindEvents: function() {
    const container = document.querySelector('.item_choice_project_container');
    if (!container) {
        console.error('Контейнер проектов не найден');
        return;
    }

    // Делегирование событий
    container.addEventListener('click', (e) => {
        const projectItem = e.target.closest('.project-item');
        if (!projectItem) return;
        
        const icon = this.findProjectIcon(projectItem);
        if (!icon) return;

        if (e.target.closest('.close-icon') || 
            e.target.closest('#add_close_icon') || 
            e.target.closest('.project-content')) {
        this.toggleProjectSelection(projectItem, icon);
        }
    });
    
    // Обработчик кнопки отправки
    const submitBtn = document.getElementById('button_filter_submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.submitSelectedProjects();
        });
    } else {
        console.error('Кнопка button_filter_submit не найдена');
    }
    },
    
    // Поиск иконки в элементе проекта
    findProjectIcon: function(projectItem) {
    return projectItem.querySelector('.close-icon') || 
            projectItem.querySelector('#add_close_icon');
    },
    
    toggleProjectSelection: function(projectItem, icon) {
    const projectIdEl = projectItem.querySelector('.id_position_unic_project');
    if (!projectIdEl) {
        console.error('ID проекта не найден');
        return;
    }
    
    const projectId = projectIdEl.textContent;
    
    if (this.selectedProjects.has(projectId)) {
        this.deselectProject(projectItem, icon);
    } else {
        this.selectProject(projectItem, icon, projectId);
    }
    },
    
    selectProject: function(projectItem, icon, projectId) {
    this.selectedProjects.add(projectId);
    projectItem.classList.add('selected');
    icon.src = staticUrls.closeIcon;
    icon.classList.add('selected');
    },
    
    deselectProject: function(projectItem, icon) {
    const projectIdEl = projectItem.querySelector('.id_position_unic_project');
    if (projectIdEl) {
        this.selectedProjects.delete(projectIdEl.textContent);
    }
    projectItem.classList.remove('selected');
    icon.src = staticUrls.addIcon;
    icon.classList.remove('selected');
    },
    
    submitSelectedProjects: function() {
    if (this.selectedProjects.size === 0) {
        alert('Выберите хотя бы один проект');
        return;
    }
    
    fetch('/finder/add_projects_to_session/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCSRFToken(),
        },
        body: JSON.stringify({
        projects_ids: Array.from(this.selectedProjects)
        }),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сервера');
        this.clearSelections();
        this.closePopup();
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось сохранить проекты');
    });
    },
    
    clearSelections: function() {
    this.selectedProjects.clear();
    document.querySelectorAll('.project-item').forEach(item => {
        const icon = this.findProjectIcon(item);
        if (icon) {
        item.classList.remove('selected');
        icon.src = staticUrls.addIcon;
        icon.classList.remove('selected');
        }
    });
    },
    
    closePopup: function() {
    const popup = document.querySelector('.choice_project_popup');
    if (popup) popup.style.display = 'none';
    },
    
    getCSRFToken: function() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
    }
};

projectSelection.init();
});