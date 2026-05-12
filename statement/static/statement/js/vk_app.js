// ============================================
// vk_app.js - УПРОЩЕННАЯ ВЕРСИЯ С АВТОДОПОЛНЕНИЕМ
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
    const projectSearchInput = document.getElementById('projectSearchInput');
    const projectSuggestList = document.getElementById('projectSuggestList');
    const multiselectContainer = document.getElementById('multiselectContainer');
    
    // Состояние
    let vkFiles = [];           // Массив файлов из индекса
    let projects = [];
    let selectedVK = null;      // Выбранный файл
    let selectedProjects = [];
    let searchTimeout = null;
    let isLoading = false;
    
    // ============================================
    // СОЗДАЕМ КОНТЕЙНЕР ДЛЯ ДИАПАЗОНА СТРОК
    // ============================================
    
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
                <input type="number" id="startRow" min="1" value="11" 
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
    
    if (projectsPanel && projectsPanel.parentNode) {
        projectsPanel.parentNode.insertBefore(rangeContainer, projectsPanel.nextSibling);
    }
    
    const startRowInput = document.getElementById('startRow');
    const endRowInput = document.getElementById('endRow');
    
    // ============================================
    // ЗАГРУЗКА ФАЙЛОВ ИЗ ИНДЕКСА
    // ============================================
    
    async function loadIndexedFiles(searchQuery = '') {
        if (isLoading) return;
        
        isLoading = true;
        
        try {
            let url = '/statement/api/smb/files/?page_size=200';
            if (searchQuery) {
                url += `&search=${encodeURIComponent(searchQuery)}`;
            }
            
            console.log('🔄 Загружаем файлы из индекса:', url);
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                vkFiles = data.files || [];
                console.log(`✅ Загружено ${vkFiles.length} файлов`);
                
                if (searchQuery) {
                    showVkSuggestions(vkFiles);
                }
                
                return true;
            } else {
                console.error('❌ Ошибка загрузки:', data.error);
                vkFiles = [];
                return false;
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки:', error);
            vkFiles = [];
            return false;
        } finally {
            isLoading = false;
        }
    }
    
    // ============================================
    // АВТОДОПОЛНЕНИЕ ПРИ ВВОДЕ
    // ============================================
    
    if (vkInput) {
        vkInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (searchTimeout) clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                if (query.length >= 2) {  // Начинаем поиск при 2+ символах
                    loadIndexedFiles(query);
                } else if (query.length === 0) {
                    // Если поле пустое, показываем последние 20 файлов
                    loadIndexedFiles('');
                } else {
                    if (vkList) vkList.style.display = 'none';
                }
            }, 300);
        });
        
        vkInput.addEventListener('focus', function() {
            if (vkFiles.length > 0) {
                showVkSuggestions(vkFiles.slice(0, 30));
            } else {
                loadIndexedFiles('');
            }
        });
        
        // Закрытие списка при клике вне
        document.addEventListener('click', function(e) {
            if (vkInput && !vkInput.contains(e.target) && vkList && !vkList.contains(e.target)) {
                vkList.style.display = 'none';
            }
        });
    }
    
    function showVkSuggestions(files) {
        if (!vkList) return;
        
        vkList.innerHTML = '';
        
        if (!files || files.length === 0) {
            vkList.style.display = 'none';
            return;
        }
        
        // Ограничиваем количество показываемых файлов
        const displayFiles = files.slice(0, 50);
        const fragment = document.createDocumentFragment();
        
        displayFiles.forEach(file => {
            const li = document.createElement('li');
            
            // Получаем текущий поисковый запрос для подсветки
            const searchQuery = vkInput.value.trim();
            let displayName = file.filename;
            
            if (searchQuery) {
                const regex = new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                displayName = file.filename.replace(regex, '<mark>$1</mark>');
            }
            
            // Показываем относительный путь если есть
            const pathInfo = file.relative_path && file.relative_path !== file.filename 
                ? `<span style="font-size: 0.7rem; color: #999; margin-left: 8px;">📁 ${file.relative_path}</span>`
                : '';
            
            li.innerHTML = `
                <span class="material-icons" style="color: #667eea;">description</span>
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${displayName}
                </span>
                ${pathInfo}
            `;
            
            li.title = file.filename; // Подсказка при наведении
            
            li.dataset.id = file.id;
            li.dataset.path = file.path;
            li.dataset.name = file.filename;
            li.dataset.relativePath = file.relative_path || '';
            
            li.addEventListener('click', () => selectVK({
                id: file.id,
                name: file.filename,
                path: file.path,
                relative_path: file.relative_path || ''
            }));
            
            fragment.appendChild(li);
        });
        
        vkList.appendChild(fragment);
        vkList.style.display = 'block';
        
        // Если файлов много, показываем счетчик
        if (files.length > 50) {
            const counter = document.createElement('li');
            counter.style.cssText = `
                text-align: center;
                color: #666;
                font-size: 0.8rem;
                padding: 8px;
                background: #f9f9f9;
                border-top: 1px solid #eee;
            `;
            counter.textContent = `Показано 50 из ${files.length} файлов. Уточните поиск.`;
            vkList.appendChild(counter);
        }
    }
    
    function selectVK(file) {
        selectedVK = {
            id: file.id,
            name: file.name,
            path: file.path,
            relative_path: file.relative_path || ''
        };
        
        if (selectedVKName) {
            selectedVKName.textContent = file.name;
        }
        
        if (selectedVKChip) {
            selectedVKChip.style.display = 'inline-flex';
        }
        
        if (vkInput) {
            vkInput.value = file.name;
        }
        
        if (vkList) {
            vkList.style.display = 'none';
        }
        
        // Показываем путь к файлу если он в подпапке
        if (file.relative_path && file.relative_path !== file.name) {
            const existingInfo = document.getElementById('selectedVKPathInfo');
            if (existingInfo) existingInfo.remove();
            
            const pathInfo = document.createElement('div');
            pathInfo.id = 'selectedVKPathInfo';
            pathInfo.style.cssText = `
                font-size: 0.75rem;
                color: #666;
                margin-top: 6px;
                padding: 4px 8px;
                background: #f5f7fa;
                border-radius: 6px;
                display: inline-block;
            `;
            pathInfo.innerHTML = `📁 ${file.relative_path}`;
            
            if (selectedVKName && selectedVKName.parentElement) {
                selectedVKName.parentElement.appendChild(pathInfo);
                setTimeout(() => pathInfo.remove(), 5000);
            }
        }
        
        // Показываем панель проектов и диапазон строк
        if (projectsPanel) {
            projectsPanel.classList.add('visible');
        }
        
        if (rangeContainer) {
            rangeContainer.style.display = 'block';
        }
        
        // Сбрасываем выбранные проекты
        selectedProjects = [];
        renderSelectedProjects();
        
        // Сбрасываем диапазон на значения по умолчанию
        if (startRowInput) startRowInput.value = '11';
        if (endRowInput) endRowInput.value = '50';
        
        updateFillButton();
        
        console.log('✅ Выбран файл:', selectedVK);
        showNotification(`Выбран файл: ${file.name}`, 'success');
    }
    
    // ============================================
    // ПОИСК И ВЫБОР ПРОЕКТОВ
    // ============================================
    
    let projectSearchTimeout = null;
    
    if (projectSearchInput) {
        projectSearchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            if (projectSearchTimeout) clearTimeout(projectSearchTimeout);
            
            projectSearchTimeout = setTimeout(() => {
                if (projects.length === 0) {
                    loadProjects();
                    return;
                }
                
                const filtered = projects.filter(projectObj => {
                    if (selectedProjects.some(p => p.id === projectObj.id)) {
                        return false;
                    }
                    const projectNumber = String(projectObj.project || '').toLowerCase();
                    return projectNumber.includes(query);
                });
                
                showProjectSuggestions(filtered.slice(0, 50));
            }, 200);
        });
        
        projectSearchInput.addEventListener('focus', function() {
            if (projects.length > 0) {
                const filtered = projects.filter(p => !selectedProjects.some(sp => sp.id === p.id));
                showProjectSuggestions(filtered.slice(0, 50));
            } else {
                loadProjects();
            }
        });
        
        // Закрытие списка проектов при клике вне
        document.addEventListener('click', function(e) {
            if (projectSearchInput && !projectSearchInput.contains(e.target) && 
                projectSuggestList && !projectSuggestList.contains(e.target) && 
                multiselectContainer && !multiselectContainer.contains(e.target)) {
                if (projectSuggestList) projectSuggestList.style.display = 'none';
            }
        });
    }
    
    function showProjectSuggestions(projectsList) {
        if (!projectSuggestList) return;
        
        projectSuggestList.innerHTML = '';
        
        if (projectsList.length === 0) {
            projectSuggestList.style.display = 'none';
            return;
        }
        
        const fragment = document.createDocumentFragment();
        
        projectsList.forEach(projectObj => {
            const li = document.createElement('li');
            const statusDot = projectObj.status_color ? 
                `<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${projectObj.status_color}; margin-right:8px;"></span>` : '';
            
            li.innerHTML = `
                <span class="material-icons">folder</span>
                <span style="display:flex; align-items:center; gap: 4px;">
                    ${statusDot}
                    <strong>${projectObj.project}</strong>
                    <span style="color: #999; font-size: 0.8rem;">(id: ${projectObj.id})</span>
                </span>
            `;
            li.addEventListener('click', () => addProject(projectObj));
            fragment.appendChild(li);
        });
        
        projectSuggestList.appendChild(fragment);
        projectSuggestList.style.display = 'block';
    }
    
    function addProject(projectObj) {
        if (!selectedProjects.some(p => p.id === projectObj.id)) {
            selectedProjects.push(projectObj);
            renderSelectedProjects();
            if (projectSearchInput) {
                projectSearchInput.value = '';
                projectSearchInput.focus();
            }
            updateFillButton();
            console.log('✅ Добавлен проект:', projectObj.project);
            showNotification(`Добавлен проект: ${projectObj.project}`, 'success');
        }
    }
    
    function removeProject(projectObj) {
        selectedProjects = selectedProjects.filter(p => p.id !== projectObj.id);
        renderSelectedProjects();
        updateFillButton();
        console.log('❌ Удален проект:', projectObj.project);
    }
    
    function renderSelectedProjects() {
        if (!multiselectContainer) return;
        
        // Очищаем контейнер, но сохраняем input
        const savedInput = multiselectContainer.querySelector('#projectSearchInput');
        multiselectContainer.innerHTML = '';
        
        selectedProjects.forEach(projectObj => {
            const chip = document.createElement('span');
            chip.className = 'selected-project-tag';
            
            const statusColor = projectObj.status_color || '#9e9e9e';
            
            chip.innerHTML = `
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${statusColor}; margin-right:6px;"></span>
                ${projectObj.project}
                <span class="material-icons" style="font-size: 16px; cursor: pointer; margin-left: 6px;">close</span>
            `;
            
            chip.querySelector('.material-icons').addEventListener('click', (e) => {
                e.stopPropagation();
                removeProject(projectObj);
            });
            
            multiselectContainer.appendChild(chip);
        });
        
        // Возвращаем input обратно
        if (projectSearchInput) {
            multiselectContainer.appendChild(projectSearchInput);
            projectSearchInput.placeholder = selectedProjects.length ? 'Добавить еще проект...' : 'Введите номер проекта...';
            projectSearchInput.style.flex = '1';
            projectSearchInput.style.minWidth = '180px';
        }
    }
    
    // ============================================
    // ЗАГРУЗКА ПРОЕКТОВ
    // ============================================
    
    async function loadProjects() {
        try {
            console.log('🔄 Загружаем проекты...');
            const response = await fetch('/finder/get_all_projects/');
            const data = await response.json();
            
            if (Array.isArray(data)) {
                projects = data;
            } else if (data.results && Array.isArray(data.results)) {
                projects = data.results;
            } else if (data.data && Array.isArray(data.data)) {
                projects = data.data;
            } else {
                projects = [];
            }
            
            console.log(`✅ Загружено ${projects.length} проектов`);
        } catch (error) {
            console.error('❌ Ошибка загрузки проектов:', error);
            projects = [];
        }
    }
    
    // ============================================
    // ВАЛИДАЦИЯ ДИАПАЗОНА СТРОК
    // ============================================
    
    function validateRowRange() {
        const start = parseInt(startRowInput ? startRowInput.value : 2);
        const end = parseInt(endRowInput ? endRowInput.value : 50);
        
        if (isNaN(start) || start < 1) {
            if (startRowInput) startRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Начальная строка должна быть >= 1' };
        } else {
            if (startRowInput) startRowInput.style.borderColor = '#dce3ec';
        }
        
        if (isNaN(end)) {
            // end может быть пустым - значит до конца
            return { valid: true, start, end: null };
        }
        
        if (end < 1) {
            if (endRowInput) endRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Конечная строка должна быть >= 1' };
        } else {
            if (endRowInput) endRowInput.style.borderColor = '#dce3ec';
        }
        
        if (start > end) {
            if (startRowInput) startRowInput.style.borderColor = '#f44336';
            if (endRowInput) endRowInput.style.borderColor = '#f44336';
            return { valid: false, error: 'Начальная строка не может быть больше конечной' };
        }
        
        return { valid: true, start, end: end };
    }
    
    // ============================================
    // ОТПРАВКА ДАННЫХ
    // ============================================
    
    if (fillBtn) {
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
            
            console.log('📤 Отправка данных:');
            console.log('   File ID:', selectedVK.id);
            console.log('   File name:', selectedVK.name);
            console.log('   Projects:', selectedProjects.map(p => p.project));
            console.log('   Range:', rangeValidation.start, '-', rangeValidation.end || 'конец');
            
            fillBtn.disabled = true;
            fillBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Заполнение...';
            
            try {
                const requestData = {
                    file_id: selectedVK.id,
                    vk_file: selectedVK.name,
                    projects: selectedProjects.map(p => ({
                        id: p.id,
                        project: p.project
                    })),
                    start_row: rangeValidation.start,
                    end_row: rangeValidation.end
                };
                
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
                    // Показываем результат
                    if (resultContainer) {
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
                        
                        // Информация о файле
                        const fileInfo = document.createElement('div');
                        fileInfo.style.cssText = `
                            font-size: 0.85rem;
                            color: #4b6589;
                            margin-bottom: 8px;
                            padding: 6px 10px;
                            background: #f0f5ff;
                            border-radius: 6px;
                        `;
                        fileInfo.innerHTML = `
                            📄 Исходный файл: <strong>${selectedVK.name}</strong>
                            ${selectedVK.relative_path ? `<br>📁 Папка: ${selectedVK.relative_path}` : ''}
                        `;
                        resultContainer.appendChild(fileInfo);
                        
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
                                const originalHTML = copyBtn.innerHTML;
                                copyBtn.innerHTML = '<span class="material-icons" style="font-size: 18px;">check</span> Скопировано!';
                                copyBtn.style.background = '#4CAF50';
                                copyBtn.style.color = 'white';
                                
                                setTimeout(() => {
                                    copyBtn.innerHTML = originalHTML;
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
                            <span>📄 Диапазон: <strong>${result.row_range || `${rangeValidation.start}-${rangeValidation.end || 'конец'}`}</strong></span>
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
                    }
                    
                    showNotification(`✅ Обработано строк: ${result.rows_processed || 0}`);
                    
                    // Опционально: сброс выбора
                    // resetSelection();
                    
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
    }
    
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
        const bgColor = type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3';
        
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
            word-break: break-word;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        `;
        
        const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
        notification.innerHTML = `<span style="font-weight: bold;">${icon}</span> ${message}`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    function updateFillButton() {
        if (fillBtn) {
            fillBtn.disabled = !(selectedVK && selectedProjects.length > 0);
        }
    }
    
    function resetSelection() {
        selectedVK = null;
        selectedProjects = [];
        if (selectedVKName) selectedVKName.textContent = '';
        if (selectedVKChip) selectedVKChip.style.display = 'none';
        if (vkInput) vkInput.value = '';
        if (projectsPanel) projectsPanel.classList.remove('visible');
        if (rangeContainer) rangeContainer.style.display = 'none';
        renderSelectedProjects();
        updateFillButton();
    }
    
    // ============================================
    // СТИЛИ
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
        #vkSuggestList {
            position: absolute;
            z-index: 1000;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            max-height: 300px;
            overflow-y: auto;
            min-width: 300px;
        }
        #vkSuggestList mark {
            background: #ffeb3b;
            padding: 0 2px;
            border-radius: 2px;
            font-weight: bold;
        }
        #vkSuggestList li {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            cursor: pointer;
            transition: background 0.2s;
            border-bottom: 1px solid #f0f0f0;
        }
        #vkSuggestList li:hover {
            background: #f5f7fa;
        }
        #vkSuggestList .material-icons {
            color: #667eea;
            font-size: 20px;
            flex-shrink: 0;
        }
        #projectSuggestList {
            position: absolute;
            z-index: 1000;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            max-height: 250px;
            overflow-y: auto;
            min-width: 280px;
        }
        #projectSuggestList li {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            cursor: pointer;
            transition: background 0.2s;
            border-bottom: 1px solid #f0f0f0;
        }
        #projectSuggestList li:hover {
            background: #f5f7fa;
        }
        #selectedVKPathInfo {
            animation: fadeInOut 5s ease;
        }
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translateY(-5px); }
            10% { opacity: 1; transform: translateY(0); }
            90% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(-5px); }
        }
        .search-container {
            position: relative;
        }
    `;
    document.head.appendChild(style);
    
    // Добавляем относительное позиционирование для контейнера поиска
    if (vkInput && vkInput.parentElement) {
        vkInput.parentElement.style.position = 'relative';
        vkInput.parentElement.classList.add('search-container');
    }
    
    // ============================================
    // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
    // ============================================
    
    // Загружаем начальный список файлов
    loadIndexedFiles('');
    
    // Загружаем проекты
    loadProjects();
});