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
    // СОЗДАЕМ ПОЛЯ ДЛЯ ДИАПАЗОНА СТРОК
    // ============================================
    
    // Контейнер для диапазона строк (добавим после выбора ВК)
    const rangeContainer = document.createElement('div');
    rangeContainer.id = 'rangeContainer';
    rangeContainer.className = 'range-container';
    rangeContainer.style.cssText = `
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(8px);
        border-radius: 32px;
        padding: 1.6rem 1.8rem;
        margin: 24px 0 28px;
        border: 1px solid rgba(255,255,255,0.9);
        box-shadow: inset 0 1px 3px white, 0 8px 18px -10px rgba(0,32,64,0.2);
        display: none;
    `;
    
    rangeContainer.innerHTML = `
        <div class="range-header" style="display: flex; align-items: center; gap: 8px; color: #0b1e33; font-weight: 600; font-size: 1rem; margin-bottom: 16px;">
            <span class="material-icons">format_list_numbered</span>
            <span>Диапазон строк для обработки</span>
        </div>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
                <label style="display: block; font-size: 0.9rem; color: #4b6589; margin-bottom: 6px;">
                    Начать со строки:
                </label>
                <input type="number" id="startRow" min="1" value="2" 
                    style="padding: 12px 16px; border: 1px solid #dce3ec; border-radius: 20px; font-size: 1rem; outline: none; transition: all 0.15s;">
            </div>
            <div style="flex: 1; min-width: 200px;">
                <label style="display: block; font-size: 0.9rem; color: #4b6589; margin-bottom: 6px;">
                    Закончить на строке:
                </label>
                <input type="number" id="endRow" min="1" value="50"
                    style="padding: 12px 16px; border: 1px solid #dce3ec; border-radius: 20px; font-size: 1rem; outline: none; transition: all 0.15s;">
            </div>
        </div>
        <div style="margin-top: 12px; font-size: 0.85rem; color: #f57c00; display: flex; align-items: center; gap: 6px;">
            <span class="material-icons" style="font-size: 1.1rem;">info</span>
            <span>Укажите диапазон строк. Первая строка обычно заголовок.</span>
        </div>
    `;
    
    // Вставляем после панели проектов
    projectsPanel.parentNode.insertBefore(rangeContainer, projectsPanel.nextSibling);
    
    // Получаем ссылки на поля диапазона
    const startRowInput = document.getElementById('startRow');
    const endRowInput = document.getElementById('endRow');
    
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
        
        // Показываем панель проектов и диапазон строк
        projectsPanel.classList.add('visible');
        rangeContainer.style.display = 'block';
        
        // Сбрасываем выбранные проекты
        selectedProjects = [];
        renderSelectedProjects();
        
        // Сбрасываем диапазон на значения по умолчанию
        startRowInput.value = '11';
        endRowInput.value = '50';
        
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
    // ВАЛИДАЦИЯ ДИАПАЗОНА СТРОК
    // ============================================
    
    function validateRowRange() {
        const start = parseInt(startRowInput.value);
        const end = parseInt(endRowInput.value);
        
        if (isNaN(start) || start < 1) {
            startRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Начальная строка должна быть >= 1' };
        } else {
            startRowInput.style.borderColor = '#dce3ec';
        }
        
        if (isNaN(end) || end < 1) {
            endRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Конечная строка должна быть >= 1' };
        } else {
            endRowInput.style.borderColor = '#dce3ec';
        }
        
        if (start > end) {
            startRowInput.style.borderColor = '#f44336';
            endRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Начальная строка не может быть больше конечной' };
        }
        
        return { valid: true, start, end };
    }
    
    // ============================================
    // ОТПРАВКА ДАННЫХ (JOB_VK)
    // ============================================
    
    fillBtn.addEventListener('click', async function() {
        // Валидация
        if (!selectedVK) {
            showNotification('❌ Выберите файл ВК', 'error');
            return;
        }
        
        if (!selectedProjects.length) {
            showNotification('❌ Выберите хотя бы один проект', 'error');
            return;
        }
        
        const rangeValidation = validateRowRange();
        if (!rangeValidation.valid) {
            showNotification(`❌ ${rangeValidation.error}`, 'error');
            return;
        }
        
        console.log('selectedVK:', selectedVK);
        console.log('selectedProjects:', selectedProjects);
        console.log('startRow:', rangeValidation.start);
        console.log('endRow:', rangeValidation.end);
        
        fillBtn.disabled = true;
        fillBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Заполнение...';
        
        try {
            // Подготавливаем данные для отправки
            const requestData = {
                vk_file: selectedVK,
                projects: selectedProjects.map(p => ({
                    id: p.id,
                    project: p.project
                })),
                start_row: rangeValidation.start,
                end_row: rangeValidation.end
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
                    margin-bottom: 8px;
                `;
                infoLine.innerHTML = `
                    <span>📊 Строк обработано: <strong>${result.rows_processed || 0}</strong></span>
                    <span>📄 Диапазон: <strong>${result.row_range || `${rangeValidation.start}-${rangeValidation.end}`}</strong></span>
                `;
                resultContainer.appendChild(infoLine);
                
                // Информация об удалении временной папки
                if (result.temp_folder_deleted) {
                    const cleanInfo = document.createElement('div');
                    cleanInfo.style.cssText = `
                        font-size: 0.85rem;
                        color: #4CAF50;
                        margin-top: 4px;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                    `;
                    cleanInfo.innerHTML = '<span class="material-icons" style="font-size: 16px;">delete</span> Временные файлы очищены';
                    resultContainer.appendChild(cleanInfo);
                }
                
                showNotification(`✅ Обработано строк: ${result.rows_processed || 0}`);
                
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
        .range-container input[type="number"]:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2);
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
    // ============================================
    
    loadVkFiles();
    loadProjects();
});