document.addEventListener('DOMContentLoaded', function() {
    // Элементы
    const searchInput = document.getElementById('project_search');
    const selectedProjectsContainer = document.querySelector('.selected-projects-container');
    const filterSubmitButton = document.getElementById('button_filter_submit');
    const clearFilterButton = document.querySelector('.button_wrapper_clear');
    
    let allProjects = [];

    // 1. Логика для попапа выбора проектов
    function renderProjects(projects) {
        const container = document.querySelector('.item_choice_project_container');
        if (!container) return;
        
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
                <div class="id_position_unic_project" hidden>${project.id}</div>
            `;
            
            container.appendChild(projectElement);
        });
    }

    function filterProjects() {
        const searchTerm = searchInput?.value.toLowerCase().trim() || '';
        
        if (!Array.isArray(allProjects)) {
            console.error('allProjects is not an array');
            return;
        }
        
        const filteredProjects = searchTerm 
            ? allProjects.filter(project => 
                project?.project && String(project.project).toLowerCase().includes(searchTerm))
            : allProjects;
        
        renderProjects(filteredProjects);
    }

    async function loadProjectsIntoPopup() {
        try {
            const container = document.querySelector('.item_choice_project_container');
            if (!container) return;
            
            container.innerHTML = '<div>Загрузка проектов...</div>';
            
            const response = await fetch('/finder/get_all_projects/');
            if (!response.ok) throw new Error(`Ошибка HTTP: ${response.status}`);
            
            allProjects = await response.json();
            filterProjects();
        } catch (error) {
            console.error('Ошибка:', error);
            const container = document.querySelector('.item_choice_project_container');
            if (container) container.innerHTML = '<div>Ошибка загрузки проектов</div>';
        }
    }

    // 2. Логика для выбранных проектов
    async function loadSelectedProjects() {
        try {
            const response = await fetch('/finder/get_session_filter_projects/');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            displaySelectedProjects(data.selected_projects || []);
        } catch (error) {
            console.error('Ошибка загрузки проектов:', error);
            if (selectedProjectsContainer) {
                selectedProjectsContainer.innerHTML = '<div class="error-message">Ошибка загрузки проектов</div>';
            }
        }
    }

    function displaySelectedProjects(projects) {
        if (!selectedProjectsContainer) return;
        
        selectedProjectsContainer.innerHTML = '';
        
        projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'project-chip';
            projectElement.dataset.projectId = project.id;
            
            projectElement.innerHTML = `
                <div class="project-chip-color" style="background-color: ${project.status_color}"></div>
                <span class="project-name">${project.project}</span>
                <button class="delete-project">&times;</button>
            `;
            
            selectedProjectsContainer.appendChild(projectElement);
        });
    }

    function handleProjectDelete(event) {
        const deleteButton = event.target.closest('.delete-project');
        if (!deleteButton) return;
        
        const projectElement = deleteButton.closest('.project-chip');
        if (!projectElement) return;
        
        const projectId = projectElement.dataset.projectId;
        if (!projectId) return;
        
        projectElement.classList.add('removing');
        
        fetch(`/finder/remove_project_from_session/${projectId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сервера');
            setTimeout(() => projectElement.remove(), 300);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            projectElement.classList.remove('removing');
        });
    }

    // 3. Вспомогательные функции
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // 4. Инициализация событий
    if (searchInput) {
        searchInput.addEventListener('input', filterProjects);
    }

    document.addEventListener('click', handleProjectDelete);

    if (filterSubmitButton) {
        filterSubmitButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (selectedProjectsContainer) {
                selectedProjectsContainer.innerHTML = '<div class="loading">Загрузка проектов...</div>';
            }
            
            const button = e.currentTarget;
            const originalText = button.textContent;
            button.disabled = true;
            button.innerHTML = '<span class="loader"></span> Обработка...';
            
            setTimeout(async () => {
                try {
                    await loadSelectedProjects();
                } catch (error) {
                    console.error('Ошибка:', error);
                } finally {
                    button.disabled = false;
                    button.textContent = originalText;
                }
            }, 1000);
        });
    }

    if (clearFilterButton) {
        clearFilterButton.addEventListener('click', async function() {
            try {
                const container = document.querySelector('.selected-projects-container');
                if (container) {
                    container.querySelectorAll('.project-chip').forEach(item => {
                        item.classList.add('removing');
                    });
                }

                const response = await fetch('/finder/clear_all_selected_projects/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include'
                });

                if (!response.ok) throw new Error('Ошибка сервера');

                setTimeout(() => {
                    if (container) container.innerHTML = '';
                }, 300);
            } catch (error) {
                console.error('Ошибка очистки проектов:', error);
                document.querySelectorAll('.project-chip.removing').forEach(item => {
                    item.classList.remove('removing');
                });
            }
        });
    }

    // 5. Делаем функции доступными глобально для popups.js
    window.loadProjectsIntoPopup = loadProjectsIntoPopup;
    
    // Инициализация при загрузке
    loadSelectedProjects();
});