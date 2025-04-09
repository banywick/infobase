document.addEventListener('DOMContentLoaded', function() {
    // Элементы popup
    const popup = document.querySelector('.choice_project_popup');
    const closeButtons = document.querySelectorAll('.close, .button_wrapper_close');
    const filterButton = document.getElementById('button_filter_projects');
    const searchInput = document.getElementById('project_search');
    let allProjects = []; // Здесь будем хранить все проекты

    // Функция для отрисовки проектов
    function renderProjects(projects) {
        const container = document.querySelector('.item_choice_project_container');
        container.innerHTML = '';
        
        projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'project-item';
            
            projectElement.innerHTML = `
                <div class="project-content">
                    <div class="circle" id="project_color" style="background-color: ${project.status_color};"></div>
                    <span>${project.project}</span>
                </div>
                <img id="add_close_icon" src="${staticUrls.addIcon}" alt="">
            `;
            
            container.appendChild(projectElement);
        });
    }
    
    // Улучшенная функция фильтрации
    function filterProjects() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        // Если нет проектов для фильтрации
        if (!Array.isArray(allProjects)) {
            console.error('allProjects is not an array');
            return;
        }
        
        // Если поле поиска пустое - показываем все проекты
        if (!searchTerm) {
            renderProjects(allProjects);
            return;
        }
        
        // Фильтрация с проверкой наличия поля project
        const filteredProjects = allProjects.filter(project => {
            try {
                // Проверяем что project существует и имеет свойство project
                if (!project || !project.project) return false;
                
                // Приводим к строке на случай если project.project не строка
                const projectName = String(project.project).toLowerCase();
                return projectName.includes(searchTerm);
            } catch (e) {
                console.error('Error filtering project:', project, e);
                return false;
            }
        });
        
        renderProjects(filteredProjects);
    }


    async function loadProjectsIntoPopup() {
        try {
            const container = document.querySelector('.item_choice_project_container');
            container.innerHTML = '<div>Загрузка проектов...</div>';
            
            const response = await fetch('/finder/get_all_projects/');
            
            if (!response.ok) throw new Error(`Ошибка HTTP: ${response.status}`);
            
            allProjects = await response.json(); // Сохраняем все проекты
            filterProjects(); // Первоначальная отрисовка (учитывает текст в поле поиска, если он есть)
            console.log(allProjects)
            
        } catch (error) {
            console.error('Ошибка:', error);
            const container = document.querySelector('.item_choice_project_container');
            container.innerHTML = '<div>Ошибка загрузки проектов</div>';
        }
    }
    
    function openPopup() {
        popup.style.display = 'block';
        loadProjectsIntoPopup();
    }
    
    function closePopup() {
        popup.style.display = 'none';
    }
    
    if (filterButton) filterButton.addEventListener('click', openPopup);
    
    closeButtons.forEach(button => {
        button.addEventListener('click', closePopup);
    });
    
    popup.addEventListener('click', function(e) {
        if (e.target === popup) closePopup();
    });

    // Обработчик ввода в поле поиска
    searchInput.addEventListener('input', filterProjects);
});



async function loadSelectedProjects() {
    try {
        const response = await fetch('/finder/get_session_filter_projects/');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        console.log('Received projects data:', data);
        displaySelectedProjects(data.selected_projects || []);
    } catch (error) {
        console.error('Ошибка загрузки проектов:', error);
        // Можно добавить уведомление для пользователя
        const container = document.querySelector('.selected-projects-container');
        container.innerHTML = '<div class="error-message">Ошибка загрузки проектов</div>';
    }
}

// Отображение выбранных проектов из сессии
function displaySelectedProjects(projects) {
    const container = document.querySelector('.selected-projects-container');
    container.innerHTML = '';
    
    if (!projects || projects.length === 0) {
        container.innerHTML = '<div class="no-projects">Нет выбранных проектов</div>';
        return;
    }
    
    projects.forEach(project => {
        const projectElement = document.createElement('div');
        projectElement.className = 'project-chip';
        projectElement.dataset.projectId = project.id; // Сохраняем ID в data-атрибуте
        
        // Создаем цветной кружок статуса (используем цвет с бэкенда)
        const colorCircle = document.createElement('div');
        colorCircle.className = 'project-chip-color';
        colorCircle.style.backgroundColor = project.status_color;
        
        // Создаем элемент с названием проекта
        const nameElement = document.createElement('span');
        nameElement.className = 'project-name';
        nameElement.textContent = project.name;
        
        // Создаем кнопку удаления (если нужно)
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-project';
        deleteButton.innerHTML = '&times;';
        deleteButton.addEventListener('click', () => removeProjectFromSession(project.id));
        
        // Собираем элементы вместе
        projectElement.appendChild(colorCircle);
        projectElement.appendChild(nameElement);
        projectElement.appendChild(deleteButton);
        
        container.appendChild(projectElement);
    });
}

// Функция для удаления проекта из сессии (пример)
async function removeProjectFromSession(projectId) {
    try {
        const response = await fetch(`/finder/remove_project_from_session/${projectId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Обновляем список проектов на странице
            displaySelectedProjects(result.remaining_projects);
            
            // Можно добавить уведомление об успехе
            showToast('Проект успешно удален из фильтра');
        } else {
            throw new Error(result.message || 'Unknown error');
        }
    } catch (error) {
        console.error('Ошибка удаления проекта:', error);
        showToast('Ошибка при удалении проекта', 'error');
    }
}

// Вспомогательная функция для показа уведомлений
function showToast(message, type = 'success') {
    // Реализация зависит от вашей системы уведомлений
    console.log(`${type}: ${message}`);
}

// Вспомогательная функция для получения CSRF токена
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadSelectedProjects();
    
    // Можно добавить обработчик для кнопки сброса фильтров
    document.querySelector('.button_wrapper_clear')?.addEventListener('click', () => {
        fetch('/finder/clear_session_projects/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            }
        }).then(loadSelectedProjects);
    });
});