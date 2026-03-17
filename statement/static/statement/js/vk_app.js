// ============================================
// ЕДИНЫЙ ФАЙЛ: vk_app.js
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const vkInput = document.getElementById('vkSearchInput');
    const vkList = document.getElementById('vkSuggestList');
    const selectedVKChip = document.getElementById('selectedVKChip');
    const selectedVKName = document.getElementById('selectedVKName');
    const projectsPanel = document.getElementById('projectsPanel');
    const fillBtn = document.getElementById('fillBtn');
    const resultContainer = document.getElementById('resultLinkContainer');
    const excelLink = document.getElementById('excelLink');
    const projectSearchInput = document.getElementById('projectSearchInput');
    const projectSuggestList = document.getElementById('projectSuggestList');
    const multiselectContainer = document.getElementById('multiselectContainer');
    
    // Состояние
    let vkFiles = [];
    let projects = [];
    let selectedVK = null;
    let selectedProjects = [];
    
    // ============================================
    // ЗАГРУЗКА ДАННЫХ
    // ============================================
    
    async function loadVkFiles() {
        try {
            console.log('🔄 Загружаем ВК файлы...');
            const response = await fetch('/statement/get-vk-files/');
            const data = await response.json();
            
            if (data.success) {
                vkFiles = data.files || [];
                console.log('✅ ВК файлы загружены:', vkFiles.length, vkFiles);
            } else {
                console.error('❌ Ошибка загрузки ВК:', data.error);
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки ВК:', error);
        }
    }
    
    async function loadProjects() {
        try {
            console.log('🔄 Загружаем проекты...');
            const response = await fetch('/finder/get_all_projects/');
            const data = await response.json();
            
            console.log('📦 Данные проектов:', data);
            
            if (Array.isArray(data)) {
                projects = data;
                console.log('✅ Проекты загружены:', projects.length);
            } else if (data.results && Array.isArray(data.results)) {
                projects = data.results;
                console.log('✅ Проекты загружены:', projects.length);
            } else if (data.data && Array.isArray(data.data)) {
                projects = data.data;
                console.log('✅ Проекты загружены:', projects.length);
            } else {
                console.error('❌ Неизвестная структура данных:', data);
                projects = [];
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки проектов:', error);
            projects = [];
        }
    }
    
    // ============================================
    // ПОИСК И ВЫБОР ВК
    // ============================================
    
    vkInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            showVkSuggestions(vkFiles);
        } else {
            const filtered = vkFiles.filter(file => 
                file.toLowerCase().includes(query)
            );
            showVkSuggestions(filtered);
        }
    });
    
    vkInput.addEventListener('focus', function() {
        if (vkFiles.length > 0) {
            showVkSuggestions(vkFiles);
        }
    });
    
    function showVkSuggestions(files) {
        vkList.innerHTML = '';
        
        if (files.length === 0) {
            vkList.style.display = 'none';
            return;
        }
        
        files.forEach(file => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="material-icons">description</span>
                <span>${file}</span>
            `;
            li.addEventListener('click', () => selectVK(file));
            vkList.appendChild(li);
        });
        
        vkList.style.display = 'block';
    }
    
    function selectVK(file) {
        selectedVK = file;
        selectedVKName.textContent = file;
        selectedVKChip.style.display = 'inline-flex';
        vkInput.value = '';
        vkList.style.display = 'none';
        
        projectsPanel.classList.add('visible');
        
        // Сбрасываем выбранные проекты
        selectedProjects = [];
        renderSelectedProjects();
        updateFillButton();
        
        console.log('✅ Выбран ВК:', file);
    }
    
    // ============================================
    // ПОИСК И ВЫБОР ПРОЕКТОВ
    // ============================================
    
    projectSearchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (projects.length === 0) return;
        
        const filtered = projects.filter(projectObj => {
            if (selectedProjects.some(p => p.id === projectObj.id)) {
                return false;
            }
            const projectNumber = String(projectObj.project || '').toLowerCase();
            return projectNumber.includes(query);
        });
        
        showProjectSuggestions(filtered);
    });
    
    projectSearchInput.addEventListener('focus', function() {
        if (projects.length > 0) {
            const filtered = projects.filter(p => !selectedProjects.some(sp => sp.id === p.id));
            showProjectSuggestions(filtered);
        } else {
            loadProjects();
        }
    });
    
    function showProjectSuggestions(projectsList) {
        projectSuggestList.innerHTML = '';
        
        if (projectsList.length === 0) {
            projectSuggestList.style.display = 'none';
            return;
        }
        
        projectsList.forEach(projectObj => {
            const li = document.createElement('li');
            const statusDot = projectObj.status_color ? 
                `<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${projectObj.status_color}; margin-right:8px;"></span>` : '';
            
            li.innerHTML = `
                <span class="material-icons">folder</span>
                <span style="display:flex; align-items:center;">
                    ${statusDot}
                    ${projectObj.project} (id: ${projectObj.id})
                </span>
            `;
            li.addEventListener('click', () => addProject(projectObj));
            projectSuggestList.appendChild(li);
        });
        
        projectSuggestList.style.display = 'block';
    }
    
    function addProject(projectObj) {
        if (!selectedProjects.some(p => p.id === projectObj.id)) {
            selectedProjects.push(projectObj);
            renderSelectedProjects();
            projectSearchInput.value = '';
            projectSearchInput.focus();
            updateFillButton();
            console.log('✅ Добавлен проект:', projectObj.project);
        }
    }
    
    function removeProject(projectObj) {
        selectedProjects = selectedProjects.filter(p => p.id !== projectObj.id);
        renderSelectedProjects();
        updateFillButton();
        console.log('❌ Удален проект:', projectObj.project);
    }
    
    function renderSelectedProjects() {
        multiselectContainer.innerHTML = '';
        
        selectedProjects.forEach(projectObj => {
            const chip = document.createElement('span');
            chip.className = 'selected-project-tag';
            
            const statusColor = projectObj.status_color || 'gray';
            
            chip.innerHTML = `
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${statusColor}; margin-right:6px;"></span>
                ${projectObj.project}
                <span class="material-icons" style="font-size: 16px; cursor: pointer; margin-left:4px;">close</span>
            `;
            
            chip.querySelector('.material-icons').addEventListener('click', (e) => {
                e.stopPropagation();
                removeProject(projectObj);
            });
            
            multiselectContainer.appendChild(chip);
        });
        
        multiselectContainer.appendChild(projectSearchInput);
        projectSearchInput.placeholder = selectedProjects.length ? '' : 'Введите номер проекта...';
        projectSearchInput.style.flex = '1';
    }
    
    // ============================================
    // ОТПРАВКА ДАННЫХ (JOB_VK)
    // ============================================
    
    // В обработчике кнопки "Заполнить ведомость" - исправленная часть
    fillBtn.addEventListener('click', async function() {
        if (!selectedVK || !selectedProjects.length) {
            showNotification('❌ Выберите ВК и проекты', 'error');
            return;
        }
        
        fillBtn.disabled = true;
        fillBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Заполнение...';
        
        try {
            // Подготавливаем данные для отправки
            const requestData = {
                vk_file: selectedVK,
                projects: selectedProjects.map(p => ({
                    id: p.id,
                    project: p.project
                }))
            };
            
            console.log('📤 Отправляем данные:', requestData);
            
            // Отправляем запрос
            const response = await fetch('/statement/job_vk_statement/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            console.log('📥 Ответ сервера:', result);
            
            if (result.success) {
                // Показываем успех
                showNotification(`✅ Обработано строк: ${result.rows_processed}`);
                
                // Очищаем контейнер результата
                resultContainer.innerHTML = '';
                resultContainer.style.display = 'flex';
                resultContainer.style.flexDirection = 'column';
                resultContainer.style.alignItems = 'flex-start';
                
                // Заголовок
                const title = document.createElement('div');
                title.style.cssText = `
                    font-weight: 600;
                    color: #16437e;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                `;
                title.innerHTML = '<span class="material-icons">check_circle</span> Файл успешно обработан';
                resultContainer.appendChild(title);
                
                // Блок с путем для копирования
                const pathBlock = document.createElement('div');
                pathBlock.style.cssText = `
                    background: #f0f5ff;
                    border: 1px solid #b9cef0;
                    border-radius: 8px;
                    padding: 12px;
                    width: 100%;
                    word-break: break-all;
                    font-family: monospace;
                    font-size: 0.9rem;
                    margin-bottom: 10px;
                `;
                pathBlock.textContent = result.smb_result_path;
                resultContainer.appendChild(pathBlock);
                
                // Кнопка копирования
                const copyBtn = document.createElement('button');
                copyBtn.style.cssText = `
                    background: #e6edfa;
                    border: 1px solid #b9cef0;
                    border-radius: 6px;
                    padding: 8px 16px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.9rem;
                    color: #16437e;
                    margin-bottom: 10px;
                `;
                copyBtn.innerHTML = '<span class="material-icons" style="font-size: 18px;">content_copy</span> Копировать путь';
                
                copyBtn.addEventListener('click', () => {
                    navigator.clipboard.writeText(result.smb_result_path).then(() => {
                        const originalText = copyBtn.innerHTML;
                        copyBtn.innerHTML = '<span class="material-icons" style="font-size: 18px;">check</span> Скопировано!';
                        copyBtn.style.background = '#4CAF50';
                        copyBtn.style.color = 'white';
                        
                        setTimeout(() => {
                            copyBtn.innerHTML = originalText;
                            copyBtn.style.background = '#e6edfa';
                            copyBtn.style.color = '#16437e';
                        }, 2000);
                    });
                });
                
                resultContainer.appendChild(copyBtn);
                
                // Информация о результате
                const infoLine = document.createElement('div');
                infoLine.style.cssText = `
                    font-size: 0.9rem;
                    color: #4b6589;
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                `;
                infoLine.innerHTML = `
                    <span>📊 Строк обработано: <strong>${result.rows_processed}</strong></span>
                `;
                resultContainer.appendChild(infoLine);
                
            } else {
                throw new Error(result.error || 'Ошибка при обработке');
            }
            
        } catch (error) {
            console.error('❌ Ошибка:', error);
            showNotification(`❌ ${error.message}`, 'error');
        } finally {
            fillBtn.disabled = false;
            fillBtn.innerHTML = '<span class="material-icons">auto_awesome</span> Заполнить ведомость';
        }
    });
    
    // ============================================
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ============================================
    
    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Функция для уведомлений
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
            word-break: break-word;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    function updateFillButton() {
        fillBtn.disabled = !(selectedVK && selectedProjects.length > 0);
    }
    
    // ============================================
    // ОБРАБОТЧИКИ КЛИКОВ ВНЕ СПИСКОВ
    // ============================================
    
    document.addEventListener('click', function(e) {
        if (!vkInput.contains(e.target) && !vkList.contains(e.target)) {
            vkList.style.display = 'none';
        }
        if (!projectSearchInput.contains(e.target) && !projectSuggestList.contains(e.target) && !multiselectContainer.contains(e.target)) {
            projectSuggestList.style.display = 'none';
        }
    });
    
    // ============================================
    // ДОБАВЛЯЕМ СТИЛИ ДЛЯ АНИМАЦИЙ
    // ============================================
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .selected-project-tag {
            background: #e6edfa;
            border-radius: 40px;
            padding: 6px 12px 6px 16px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
            font-weight: 500;
            color: #16437e;
            border: 1px solid #b9cef0;
            margin: 2px;
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
    // ============================================
    
    loadVkFiles();
    loadProjects();
});