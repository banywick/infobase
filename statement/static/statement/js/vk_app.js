// ============================================
// ЕДИНЫЙ ФАЙЛ: vk_app.js (ПОЛНАЯ ВЕРСИЯ С ПОДДЕРЖКОЙ ВЛОЖЕННЫХ ПАПОК)
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
    let vkFiles = [];           // Массив объектов {name, path, relative_path}
    let projects = [];
    let selectedVK = null;      // Объект {name, path, relative_path}
    let selectedProjects = [];
    let searchTimeout = null;
    let isLoading = false;
    
    // ============================================
    // СОЗДАЕМ ПОЛЯ ДЛЯ ДИАПАЗОНА СТРОК
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
    
    if (projectsPanel && projectsPanel.parentNode) {
        projectsPanel.parentNode.insertBefore(rangeContainer, projectsPanel.nextSibling);
    }
    
    const startRowInput = document.getElementById('startRow');
    const endRowInput = document.getElementById('endRow');
    
    // ============================================
    // СОЗДАЕМ ЭЛЕМЕНТЫ УПРАВЛЕНИЯ ДЛЯ ПОИСКА ВК
    // ============================================
    
    if (vkInput && vkInput.parentElement) {
        const vkSearchContainer = vkInput.parentElement;
        
        // Индикатор загрузки
        const loadingIndicator = document.createElement('span');
        loadingIndicator.id = 'vkLoadingIndicator';
        loadingIndicator.style.cssText = `
            font-size: 0.8rem;
            color: #2196F3;
            margin-left: 8px;
            display: none;
        `;
        loadingIndicator.innerHTML = '<span class="material-icons" style="font-size: 14px;">sync</span> загрузка...';
        vkSearchContainer.appendChild(loadingIndicator);
        
        // Счетчик файлов
        const fileCounter = document.createElement('span');
        fileCounter.id = 'vkFileCounter';
        fileCounter.style.cssText = `
            font-size: 0.8rem;
            color: #666;
            margin-left: 8px;
            white-space: nowrap;
        `;
        fileCounter.textContent = '(загрузка...)';
        vkSearchContainer.appendChild(fileCounter);
        
        // Кнопка "Все файлы"
        const showAllBtn = document.createElement('button');
        showAllBtn.innerHTML = '<span class="material-icons" style="font-size: 18px;">list</span> Все файлы';
        showAllBtn.style.cssText = `
            background: #f0f5ff;
            border: 1px solid #b9cef0;
            border-radius: 20px;
            padding: 8px 16px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
            color: #16437e;
            margin-left: 12px;
            transition: all 0.2s;
            white-space: nowrap;
        `;
        
        showAllBtn.addEventListener('mouseenter', () => {
            showAllBtn.style.background = '#e6edfa';
            showAllBtn.style.transform = 'scale(1.02)';
        });
        
        showAllBtn.addEventListener('mouseleave', () => {
            showAllBtn.style.background = '#f0f5ff';
            showAllBtn.style.transform = 'scale(1)';
        });
        
        showAllBtn.addEventListener('click', () => {
            if (vkFiles.length > 0) {
                showVkSuggestions(vkFiles.slice(0, 100));
                vkInput.focus();
            } else {
                showNotification('Файлы еще загружаются...', 'info');
            }
        });
        
        vkSearchContainer.appendChild(showAllBtn);
        
        // Сохраняем ссылки для доступа из других функций
        window.vkLoadingIndicator = loadingIndicator;
        window.vkFileCounter = fileCounter;
    }
    
    // ============================================
    // ЗАГРУЗКА ДАННЫХ
    // ============================================
    
    async function loadVkFiles() {
        if (isLoading) return;
        
        isLoading = true;
        if (window.vkLoadingIndicator) window.vkLoadingIndicator.style.display = 'inline-block';
        
        try {
            console.log('🔄 Загружаем ВК файлы...');
            const response = await fetch('/statement/get-vk-files/');
            const data = await response.json();
            
            if (data.success) {
                vkFiles = data.files || [];
                console.log(`✅ Загружено ${vkFiles.length} файлов`);
                
                // Обновляем счетчик
                if (window.vkFileCounter) {
                    window.vkFileCounter.textContent = `(${vkFiles.length.toLocaleString()} файлов)`;
                }
                
                // Для отладки - показать примеры
                if (vkFiles.length > 0) {
                    console.log('📋 Примеры файлов:');
                    vkFiles.slice(0, 5).forEach(file => {
                        console.log(`  ${file.name} -> ${file.relative_path || 'корень'}`);
                    });
                }
            } else {
                console.error('❌ Ошибка загрузки ВК:', data.error);
                vkFiles = [];
                if (window.vkFileCounter) {
                    window.vkFileCounter.textContent = '(ошибка загрузки)';
                }
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки ВК:', error);
            vkFiles = [];
            if (window.vkFileCounter) {
                window.vkFileCounter.textContent = '(ошибка загрузки)';
            }
        } finally {
            isLoading = false;
            if (window.vkLoadingIndicator) window.vkLoadingIndicator.style.display = 'none';
        }
    }
    
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
    // ОПТИМИЗИРОВАННЫЙ ПОИСК С DEBOUNCE
    // ============================================
    
    if (vkInput) {
        vkInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            if (searchTimeout) clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                if (query.length === 0) {
                    showVkSuggestions(vkFiles.slice(0, 50));
                } else {
                    performSearch(query);
                }
            }, 300);
        });
        
        vkInput.addEventListener('focus', function() {
            if (vkFiles.length > 0) {
                showVkSuggestions(vkFiles.slice(0, 50));
            }
        });
    }
    
    function performSearch(query) {
        if (!vkFiles.length) return;
        
        const lowerQuery = query.toLowerCase();
        const results = [];
        
        // Ищем по имени файла
        for (let i = 0; i < vkFiles.length; i++) {
            const file = vkFiles[i];
            if (file.name.toLowerCase().includes(lowerQuery)) {
                results.push(file);
                if (results.length >= 200) break;
            }
        }
        
        showVkSuggestions(results);
    }
    
    function showVkSuggestions(files) {
        if (!vkList) return;
        
        vkList.innerHTML = '';
        
        if (!files || files.length === 0) {
            vkList.style.display = 'none';
            const noResults = document.createElement('div');
            noResults.style.cssText = `
                padding: 12px;
                text-align: center;
                color: #999;
                font-style: italic;
            `;
            noResults.textContent = 'Ничего не найдено';
            vkList.appendChild(noResults);
            vkList.style.display = 'block';
            return;
        }
        
        const displayFiles = files.slice(0, 100);
        const fragment = document.createDocumentFragment();
        
        displayFiles.forEach(file => {
            const li = document.createElement('li');
            
            const query = vkInput ? vkInput.value.toLowerCase().trim() : '';
            let displayName = file.name;
            
            if (query) {
                const regex = new RegExp(`(${query})`, 'gi');
                displayName = file.name.replace(regex, '<mark>$1</mark>');
            }
            
            // Показываем путь к файлу, если он в подпапке
            const pathInfo = file.relative_path && file.relative_path !== file.name 
                ? `<span style="font-size: 0.7rem; color: #999; margin-left: 8px;">📁 ${file.relative_path}</span>`
                : '';
            
            li.innerHTML = `
                <span class="material-icons">description</span>
                <span style="flex: 1;">${displayName}</span>
                ${pathInfo}
            `;
            
            li.dataset.path = file.path;
            li.dataset.name = file.name;
            li.dataset.relativePath = file.relative_path || '';
            
            li.addEventListener('click', () => selectVK(file));
            fragment.appendChild(li);
        });
        
        vkList.appendChild(fragment);
        
        if (files.length > 100) {
            const info = document.createElement('li');
            info.style.cssText = `
                text-align: center;
                color: #666;
                font-size: 0.85rem;
                padding: 8px;
                border-top: 1px solid #eee;
                background: #f9f9f9;
            `;
            info.textContent = `Показано 100 из ${files.length} результатов. Уточните поиск для лучших результатов.`;
            vkList.appendChild(info);
        }
        
        vkList.style.display = 'block';
    }
    
    function selectVK(file) {
        // Сохраняем полную информацию о файле
        selectedVK = {
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
            vkInput.value = '';
        }
        
        if (vkList) {
            vkList.style.display = 'none';
        }
        
        // Показываем дополнительную информацию о пути
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
        
        console.log('✅ Выбран ВК файл:', selectedVK);
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
                if (projects.length === 0) return;
                
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
                <span style="display:flex; align-items:center;">
                    ${statusDot}
                    ${projectObj.project} (id: ${projectObj.id})
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
        
        if (projectSearchInput) {
            multiselectContainer.appendChild(projectSearchInput);
            projectSearchInput.placeholder = selectedProjects.length ? '' : 'Введите номер проекта...';
            projectSearchInput.style.flex = '1';
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
        
        if (isNaN(end) || end < 1) {
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
        
        return { valid: true, start, end };
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
            console.log('   Файл:', selectedVK);
            console.log('   Проекты:', selectedProjects);
            console.log('   Диапазон:', rangeValidation.start, '-', rangeValidation.end);
            
            fillBtn.disabled = true;
            fillBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Заполнение...';
            
            try {
                const requestData = {
                    vk_file: selectedVK.name,
                    vk_file_path: selectedVK.path,  // Передаем полный путь для точного поиска
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
                            ${result.source_folder ? `<span>📁 Исходная папка: <strong>${result.source_folder}</strong></span>` : ''}
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
                    
                    // Сбрасываем выбор после успешной обработки (опционально)
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
        if (projectsPanel) projectsPanel.classList.remove('visible');
        if (rangeContainer) rangeContainer.style.display = 'none';
        renderSelectedProjects();
        updateFillButton();
    }
    
    // ============================================
    // ОБРАБОТЧИКИ КЛИКОВ ВНЕ СПИСКОВ
    // ============================================
    
    document.addEventListener('click', function(e) {
        if (vkInput && !vkInput.contains(e.target) && vkList && !vkList.contains(e.target)) {
            if (vkList) vkList.style.display = 'none';
        }
        if (projectSearchInput && !projectSearchInput.contains(e.target) && 
            projectSuggestList && !projectSuggestList.contains(e.target) && 
            multiselectContainer && !multiselectContainer.contains(e.target)) {
            if (projectSuggestList) projectSuggestList.style.display = 'none';
        }
    });
    
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
    `;
    document.head.appendChild(style);
    
    // ============================================
    // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
    // ============================================
    
    loadVkFiles();
    loadProjects();
});