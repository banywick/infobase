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
                    <div class="circle" id="project_color" style="background-color: ${project.color || '#ccc'};"></div>
                    <span>${project.project}</span>
                </div>
                <img class="close-icon" src="{% static 'finder/icon/close.svg' %}" alt="Удалить">
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