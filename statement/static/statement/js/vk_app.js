// ============================================
// vk_app.js - ПОЛНАЯ ВЕРСИЯ С ПОДДЕРЖКОЙ ИНДЕКСАЦИИ И АНИМАЦИЕЙ ПРОГРЕССА
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
    let vkFiles = [];
    let projects = [];
    let selectedVK = null;
    let selectedProjects = [];
    let searchTimeout = null;
    let isLoading = false;
    let progressInterval = null;
    let currentTaskId = null;
    let currentIndexingTaskId = null;
    
    // ============================================
    // СОЗДАЕМ КНОПКУ ДЛЯ ОБНОВЛЕНИЯ ГОТОВЫХ ВЕДОМОСТЕЙ
    // ============================================
    
    const refreshButtonContainer = document.createElement('div');
    refreshButtonContainer.style.cssText = `
        display: flex;
        justify-content: flex-end;
        margin-bottom: 15px;
    `;
    
    const refreshBtn = document.createElement('button');
    refreshBtn.id = 'refreshAccountingBtn';
    refreshBtn.innerHTML = `
        <span class="material-icons" style="font-size: 18px;">sync</span>
        Обновить готовые ведомости
    `;
    refreshBtn.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 30px;
        padding: 10px 20px;
        color: white;
        font-weight: 500;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    `;
    
    refreshBtn.addEventListener('mouseenter', () => {
        refreshBtn.style.transform = 'translateY(-2px)';
        refreshBtn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
    });
    
    refreshBtn.addEventListener('mouseleave', () => {
        refreshBtn.style.transform = 'translateY(0)';
        refreshBtn.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
    });
    
    // ============================================
    // КОНТЕЙНЕР ДЛЯ ПРОГРЕССА ИНДЕКСАЦИИ
    // ============================================
    
    const indexingProgressContainer = document.createElement('div');
    indexingProgressContainer.id = 'indexingProgressContainer';
    indexingProgressContainer.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin: 10px 0 20px 0;
        color: white;
        display: none;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    `;
    
    indexingProgressContainer.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="indexing-spinner" style="width: 24px; height: 24px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 0.9rem;">Обновление готовых ведомостей</div>
                    <div id="indexingProgressStatus" style="font-size: 0.75rem; opacity: 0.9;">Подготовка...</div>
                </div>
            </div>
            <div id="indexingProgressStats" style="font-size: 0.8rem; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px;">
                ⏳ Ожидание...
            </div>
        </div>
        <div style="width: 100%; background: rgba(255,255,255,0.2); border-radius: 10px; overflow: hidden; margin-bottom: 8px;">
            <div id="indexingProgressBar" style="width: 0%; height: 6px; background: white; transition: width 0.3s ease; border-radius: 10px;"></div>
        </div>
        <div id="indexingProgressDetails" style="font-size: 0.7rem; opacity: 0.8; display: flex; justify-content: space-between;">
            <span>📁 Сканирование папок...</span>
            <span id="indexingFileCount">0 файлов найдено</span>
        </div>
    `;
    
    // Находим место для вставки кнопки
    if (vkInput && vkInput.parentElement && vkInput.parentElement.parentElement) {
        const searchWrapper = vkInput.parentElement.parentElement;
        const buttonRow = document.createElement('div');
        buttonRow.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        `;
        
        const searchContainer = vkInput.parentElement;
        const originalParent = searchContainer.parentElement;
        
        buttonRow.appendChild(refreshButtonContainer);
        refreshButtonContainer.appendChild(refreshBtn);
        
        originalParent.insertBefore(buttonRow, searchContainer);
        originalParent.insertBefore(indexingProgressContainer, searchContainer);
    }
    
    // Функции для управления прогрессом индексации
    function showIndexingProgress() {
        indexingProgressContainer.style.display = 'block';
    }
    
    function hideIndexingProgress() {
        indexingProgressContainer.style.display = 'none';
        const indexingProgressBar = document.getElementById('indexingProgressBar');
        if (indexingProgressBar) indexingProgressBar.style.width = '0%';
    }
    
    function updateIndexingProgress(percent, status, stats, fileCount = null) {
        const indexingProgressBar = document.getElementById('indexingProgressBar');
        const indexingProgressStatus = document.getElementById('indexingProgressStatus');
        const indexingProgressStats = document.getElementById('indexingProgressStats');
        const indexingFileCountSpan = document.getElementById('indexingFileCount');
        
        if (indexingProgressBar) indexingProgressBar.style.width = `${percent}%`;
        if (indexingProgressStatus) indexingProgressStatus.textContent = status;
        if (indexingProgressStats) indexingProgressStats.textContent = stats;
        if (indexingFileCountSpan && fileCount !== null) {
            indexingFileCountSpan.textContent = `${fileCount} файлов найдено`;
        }
    }
    
    // Функция для обновления индекса
    async function refreshAccountingIndex() {
        if (refreshBtn.disabled) {
            showNotification('Индексация уже выполняется...', 'info');
            return;
        }
        
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <span class="material-icons" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span>
            Индексация...
        `;
        
        showIndexingProgress();
        updateIndexingProgress(5, 'Запуск индексации...', '🔄 Инициализация', 0);
        
        let checkInterval = null;
        const startTime = Date.now();
        
        try {
            const response = await fetch('/statement/api/smb/index/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    config_type: 'search',
                    force: false
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.task_id) {
                currentIndexingTaskId = data.task_id;
                console.log('✅ Задача индексации запущена, task_id:', currentIndexingTaskId);
                
                checkInterval = setInterval(async () => {
                    try {
                        const statusResponse = await fetch(`/statement/api/smb/index/task/${currentIndexingTaskId}/`);
                        const statusData = await statusResponse.json();
                        
                        console.log('Статус индексации:', statusData.status);
                        
                        if (statusData.status === 'SUCCESS') {
                            clearInterval(checkInterval);
                            updateIndexingProgress(100, '✅ Индексация завершена!', 'Готово!', statusData.result?.total_files || 0);
                            
                            await loadIndexedFiles('');
                            
                            setTimeout(() => {
                                hideIndexingProgress();
                                refreshBtn.disabled = false;
                                refreshBtn.innerHTML = `
                                    <span class="material-icons" style="font-size: 18px;">sync</span>
                                    Обновить готовые ведомости
                                `;
                                showNotification('Индексация готовых ведомостей завершена!', 'success');
                            }, 2000);
                            
                        } else if (statusData.status === 'FAILURE') {
                            clearInterval(checkInterval);
                            updateIndexingProgress(0, '❌ Ошибка индексации', statusData.error || 'Неизвестная ошибка', 0);
                            
                            setTimeout(() => {
                                hideIndexingProgress();
                                refreshBtn.disabled = false;
                                refreshBtn.innerHTML = `
                                    <span class="material-icons" style="font-size: 18px;">sync</span>
                                    Обновить готовые ведомости
                                `;
                                showNotification(`Ошибка индексации: ${statusData.error || 'Неизвестная ошибка'}`, 'error');
                            }, 3000);
                            
                        } else if (statusData.status === 'PROGRESS' && statusData.progress) {
                            const progress = statusData.progress;
                            const percent = Math.min(progress.current || 0, 95);
                            const statusText = progress.status || 'Индексация...';
                            const fileCount = progress.total_found || 0;
                            
                            const elapsed = Math.floor((Date.now() - startTime) / 1000);
                            const timeStr = elapsed > 60 ? `${Math.floor(elapsed / 60)} мин ${elapsed % 60} сек` : `${elapsed} сек`;
                            
                            updateIndexingProgress(percent, statusText, `⏱️ ${timeStr}`, fileCount);
                            
                            refreshBtn.innerHTML = `
                                <span class="material-icons" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span>
                                Индексация: ${percent}%
                            `;
                        } else if (statusData.status === 'PENDING') {
                            updateIndexingProgress(5, '⏳ Ожидание очереди...', 'Задача в очереди', 0);
                        } else if (statusData.status === 'STARTED') {
                            updateIndexingProgress(10, '🔄 Начало индексации...', 'Сканирование файлов...', 0);
                        }
                        
                    } catch (err) {
                        console.error('Ошибка при опросе статуса:', err);
                    }
                }, 1500);
                
            } else {
                throw new Error(data.error || 'Не удалось запустить индексацию');
            }
            
        } catch (error) {
            console.error('❌ Ошибка индексации:', error);
            updateIndexingProgress(0, '❌ Ошибка', error.message, 0);
            
            setTimeout(() => {
                hideIndexingProgress();
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = `
                    <span class="material-icons" style="font-size: 18px;">sync</span>
                    Обновить готовые ведомости
                `;
                showNotification(`Ошибка индексации: ${error.message}`, 'error');
            }, 3000);
        }
    }
    
    // Добавляем обработчик на кнопку
    refreshBtn.addEventListener('click', refreshAccountingIndex);
    
    // ============================================
    // СОЗДАЕМ КОНТЕЙНЕР ДЛЯ ПРОГРЕССА ОБРАБОТКИ
    // ============================================
    
    const progressContainer = document.createElement('div');
    progressContainer.id = 'progressContainer';
    progressContainer.style.cssText = `
        background: rgba(255,255,255,0.95);
        border-radius: 32px;
        padding: 1.5rem 2rem;
        margin: 20px 0;
        border: 1px solid rgba(66, 153, 225, 0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        display: none;
        position: relative;
        overflow: hidden;
    `;
    
    progressContainer.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="progress-spinner" style="width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #4299e1; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <div>
                    <div style="font-weight: 600; color: #2d3748; font-size: 1rem;">Обработка файла...</div>
                    <div id="progressStatus" style="font-size: 0.85rem; color: #718096; margin-top: 4px;">Подготовка к обработке</div>
                </div>
            </div>
            <div id="progressStats" style="font-size: 0.9rem; color: #4a5568; background: #edf2f7; padding: 6px 12px; border-radius: 20px;">
                ⏳ Ожидание...
            </div>
        </div>
        <div style="width: 100%; background: #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 12px;">
            <div id="progressBar" style="width: 0%; height: 8px; background: linear-gradient(90deg, #4299e1, #9f7aea); transition: width 0.3s ease; border-radius: 12px;"></div>
        </div>
        <div id="progressDetails" style="font-size: 0.75rem; color: #a0aec0; display: flex; justify-content: space-between;">
            <span>📊 Начато: --:--:--</span>
            <span>✅ Обработано: 0</span>
            <span>⏱️ Прошло: 0 сек</span>
        </div>
        <div id="progressCancelBtn" style="margin-top: 12px; text-align: center;">
            <button style="background: #edf2f7; border: 1px solid #cbd5e0; border-radius: 20px; padding: 6px 16px; cursor: pointer; font-size: 0.8rem; color: #e53e3e; transition: all 0.2s;">
                ❌ Отменить обработку
            </button>
        </div>
    `;
    
    // Добавляем стили для анимации
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .progress-shimmer {
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 1.5s infinite;
        }
        @keyframes shimmer {
            to { left: 100%; }
        }
    `;
    document.head.appendChild(styleSheet);
    
    if (fillBtn && fillBtn.parentNode) {
        fillBtn.parentNode.insertBefore(progressContainer, fillBtn.nextSibling);
    }
    
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    const progressStats = document.getElementById('progressStats');
    const progressDetails = document.getElementById('progressDetails');
    const cancelBtn = progressContainer.querySelector('#progressCancelBtn button');
    
    function showProgress() {
        progressContainer.style.display = 'block';
        const shimmer = document.createElement('div');
        shimmer.className = 'progress-shimmer';
        progressContainer.appendChild(shimmer);
    }
    
    function hideProgress() {
        progressContainer.style.display = 'none';
        const shimmer = progressContainer.querySelector('.progress-shimmer');
        if (shimmer) shimmer.remove();
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }
    
    function updateProgress(percent, status, stats, startTime) {
        if (progressBar) progressBar.style.width = `${percent}%`;
        if (progressStatus) progressStatus.textContent = status;
        if (progressStats) progressStats.textContent = stats;
        
        if (progressDetails && startTime) {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            const timeStr = minutes > 0 ? `${minutes} мин ${seconds} сек` : `${seconds} сек`;
            
            const startTimeStr = new Date(startTime).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            progressDetails.innerHTML = `
                <span>📊 Начато: ${startTimeStr}</span>
                <span>✅ Обработано: ${stats.match(/\d+/)?.[0] || 0}</span>
                <span>⏱️ Прошло: ${timeStr}</span>
            `;
        }
    }
    
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
        <div class="range-header" style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 8px; color: #0b1e33; font-weight: 600; font-size: 1rem;">
                <span class="material-icons">format_list_numbered</span>
                <span>Диапазон строк для обработки</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                    <input type="radio" name="rangeMode" value="auto" checked style="width: 16px; height: 16px; cursor: pointer;">
                    <span style="font-size: 0.85rem;">Автоопределение</span>
                </label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                    <input type="radio" name="rangeMode" value="manual" style="width: 16px; height: 16px; cursor: pointer;">
                    <span style="font-size: 0.85rem;">Вручную</span>
                </label>
            </div>
        </div>
        <div id="manualRangeInputs" style="display: none;">
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px;">
                    <label style="display: block; font-size: 0.9rem; color: #4b6589; margin-bottom: 6px;">
                        Начать со строки:
                    </label>
                    <input type="number" id="startRow" min="1" value="11" 
                        style="padding: 12px 16px; border: 1px solid #dce3ec; border-radius: 20px; font-size: 1rem; outline: none; transition: all 0.15s; width: 100%;">
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <label style="display: block; font-size: 0.9rem; color: #4b6589; margin-bottom: 6px;">
                        Закончить на строке:
                    </label>
                    <input type="number" id="endRow" min="1" value="50"
                        style="padding: 12px 16px; border: 1px solid #dce3ec; border-radius: 20px; font-size: 1rem; outline: none; transition: all 0.15s; width: 100%;">
                </div>
            </div>
        </div>
        <div id="autoRangeInfo" style="margin-top: 12px; font-size: 0.85rem; color: #4CAF50; display: flex; align-items: center; gap: 6px;">
            <span class="material-icons" style="font-size: 1.1rem;">auto_awesome</span>
            <span>Данные будут определены автоматически по порядковым номерам</span>
        </div>
    `;
    
    if (projectsPanel && projectsPanel.parentNode) {
        projectsPanel.parentNode.insertBefore(rangeContainer, projectsPanel.nextSibling);
    }
    
    // Получаем элементы диапазона
    const startRowInput = document.getElementById('startRow');
    const endRowInput = document.getElementById('endRow');
    const manualRangeInputs = document.getElementById('manualRangeInputs');
    const autoRangeInfo = document.getElementById('autoRangeInfo');
    const radioButtons = document.querySelectorAll('input[name="rangeMode"]');
    
    // Обработчик переключения режима
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log('🔄 Переключение режима на:', this.value);
            if (this.value === 'auto') {
                manualRangeInputs.style.display = 'none';
                autoRangeInfo.style.display = 'flex';
            } else {
                manualRangeInputs.style.display = 'block';
                autoRangeInfo.style.display = 'none';
            }
        });
    });
    
    // ============================================
    // СОЗДАЕМ UI ДЛЯ СТАТИСТИКИ
    // ============================================
    
    if (vkInput && vkInput.parentElement) {
        vkInput.parentElement.style.position = 'relative';
        vkInput.parentElement.classList.add('search-container');
        
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
        vkInput.parentElement.appendChild(loadingIndicator);
        
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
        vkInput.parentElement.appendChild(fileCounter);
        
        // Статистика
        const statsDiv = document.createElement('div');
        statsDiv.id = 'indexStats';
        statsDiv.style.cssText = `
            font-size: 0.7rem;
            color: #888;
            margin-top: 4px;
        `;
        vkInput.parentElement.appendChild(statsDiv);
        
        window.vkLoadingIndicator = loadingIndicator;
        window.vkFileCounter = fileCounter;
    }
    
    // ============================================
    // ЗАГРУЗКА ФАЙЛОВ ИЗ ИНДЕКСА (ВСЕ КОНФИГУРАЦИИ)
    // ============================================
    
    async function loadIndexedFiles(searchQuery = '') {
        if (isLoading) return;
        
        isLoading = true;
        if (window.vkLoadingIndicator) window.vkLoadingIndicator.style.display = 'inline-block';
        
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
                console.log(`✅ Загружено ${vkFiles.length} файлов из ${data.active_configs_count || data.configs?.length || 1} конфигураций`);
                
                if (data.configs && data.configs.length > 0) {
                    console.log('📁 Конфигурации:');
                    data.configs.forEach(config => {
                        console.log(`   - ${config.name}: ${config.file_count} файлов`);
                    });
                }
                
                if (window.vkFileCounter) {
                    const total = data.total || vkFiles.length;
                    const configsCount = data.active_configs_count || data.configs?.length || 1;
                    if (configsCount > 1) {
                        window.vkFileCounter.textContent = `(${total} файлов, ${configsCount} директорий)`;
                    } else {
                        window.vkFileCounter.textContent = `(${total} файлов)`;
                    }
                }
                
                await loadIndexStats();
                
                if (!searchQuery && vkInput && document.activeElement === vkInput) {
                    showVkSuggestions(vkFiles.slice(0, 30));
                } else if (searchQuery) {
                    showVkSuggestions(vkFiles);
                }
                
                return true;
            } else {
                console.error('❌ Ошибка загрузки:', data.error);
                vkFiles = [];
                if (window.vkFileCounter) window.vkFileCounter.textContent = '(ошибка загрузки)';
                return false;
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки:', error);
            vkFiles = [];
            return false;
        } finally {
            isLoading = false;
            if (window.vkLoadingIndicator) window.vkLoadingIndicator.style.display = 'none';
        }
    }
    
    async function loadIndexStats() {
        try {
            const response = await fetch('/statement/api/smb/process/stats/');
            const data = await response.json();
            
            if (data.success && data.configs) {
                const statsContainer = document.getElementById('indexStats');
                if (statsContainer) {
                    const configCount = data.configs.length;
                    const totalFiles = data.total_files || 0;
                    
                    if (configCount > 1) {
                        statsContainer.innerHTML = `
                            <span>📊 Индексировано: ${totalFiles} файлов в ${configCount} папках</span>
                        `;
                    } else if (configCount === 1 && data.configs[0]) {
                        statsContainer.innerHTML = `
                            <span>📁 ${data.configs[0].name}: ${totalFiles} файлов</span>
                        `;
                    } else {
                        statsContainer.innerHTML = '';
                    }
                }
                return data;
            }
        } catch (error) {
            console.error('Ошибка загрузки статистики:', error);
        }
        return null;
    }
    
    // ============================================
    // АВТОДОПОЛНЕНИЕ ПРИ ВВОДЕ
    // ============================================
    
    if (vkInput) {
        vkInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (searchTimeout) clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                if (query.length >= 2) {
                    loadIndexedFiles(query);
                } else if (query.length === 0) {
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
        
        const displayFiles = files.slice(0, 50);
        const fragment = document.createDocumentFragment();
        const configNames = new Set(displayFiles.map(f => f.config?.name).filter(Boolean));
        
        displayFiles.forEach(file => {
            const li = document.createElement('li');
            
            const searchQuery = vkInput.value.trim();
            let displayName = file.filename;
            
            if (searchQuery) {
                const regex = new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                displayName = file.filename.replace(regex, '<mark>$1</mark>');
            }
            
            const configInfo = file.config ? 
                `<span style="font-size: 0.65rem; background: #e8f0fe; color: #1967d2; padding: 2px 6px; border-radius: 12px; margin-left: 8px; white-space: nowrap;">
                    📁 ${file.config.name.length > 20 ? file.config.name.substring(0, 20) + '...' : file.config.name}
                </span>` : '';
            
            const pathInfo = file.relative_path && file.relative_path !== file.filename ? 
                `<span style="font-size: 0.7rem; color: #999; margin-left: 8px;" title="${file.relative_path}">
                    📂 ${file.relative_path.length > 30 ? '...' + file.relative_path.slice(-27) : file.relative_path}
                </span>` : '';
            
            li.innerHTML = `
                <span class="material-icons" style="color: #667eea; flex-shrink: 0;">description</span>
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${displayName}
                </span>
                ${configInfo}
                ${pathInfo}
            `;
            
            li.title = `${file.filename}\nКонфигурация: ${file.config?.name || 'Неизвестно'}\nПуть: ${file.path}`;
            
            li.dataset.id = file.id;
            li.dataset.path = file.path;
            li.dataset.name = file.filename;
            li.dataset.relativePath = file.relative_path || '';
            li.dataset.configId = file.config?.id;
            li.dataset.configName = file.config?.name;
            
            li.addEventListener('click', () => selectVK({
                id: file.id,
                name: file.filename,
                path: file.path,
                relative_path: file.relative_path || '',
                config: file.config
            }));
            
            fragment.appendChild(li);
        });
        
        vkList.appendChild(fragment);
        vkList.style.display = 'block';
        
        if (configNames.size > 1) {
            const infoFooter = document.createElement('li');
            infoFooter.style.cssText = `
                text-align: center;
                color: #666;
                font-size: 0.7rem;
                padding: 6px;
                background: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            `;
            infoFooter.textContent = `Файлы из ${configNames.size} директорий. Показано ${displayFiles.length} из ${files.length}`;
            vkList.appendChild(infoFooter);
        } else if (files.length > 50) {
            const infoFooter = document.createElement('li');
            infoFooter.style.cssText = `
                text-align: center;
                color: #666;
                font-size: 0.7rem;
                padding: 6px;
                background: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            `;
            infoFooter.textContent = `Показано 50 из ${files.length} файлов. Уточните поиск.`;
            vkList.appendChild(infoFooter);
        }
    }
    
    function selectVK(file) {
        selectedVK = {
            id: file.id,
            name: file.name,
            path: file.path,
            relative_path: file.relative_path || '',
            config: file.config
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
        
        let infoHtml = '';
        if (file.config) {
            infoHtml += `<span style="background: #e8f0fe; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">
                📁 ${file.config.name}
            </span>`;
        }
        if (file.relative_path && file.relative_path !== file.name) {
            infoHtml += `<span style="margin-left: 8px;">📂 ${file.relative_path}</span>`;
        }
        
        if (infoHtml) {
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
                display: inline-flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            `;
            pathInfo.innerHTML = infoHtml;
            
            if (selectedVKName && selectedVKName.parentElement) {
                selectedVKName.parentElement.appendChild(pathInfo);
                setTimeout(() => pathInfo.remove(), 5000);
            }
        }
        
        if (projectsPanel) {
            projectsPanel.classList.add('visible');
        }
        
        if (rangeContainer) {
            rangeContainer.style.display = 'block';
        }
        
        selectedProjects = [];
        renderSelectedProjects();
        
        if (startRowInput) startRowInput.value = '';
        if (endRowInput) endRowInput.value = '';
        
        updateFillButton();
        
        console.log('✅ Выбран файл:', selectedVK);
        showNotification(`Выбран файл: ${file.name}${file.config ? ` (${file.config.name})` : ''}`, 'success');
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
    // ОПРЕДЕЛЕНИЕ РЕЖИМА ДИАПАЗОНА СТРОК
    // ============================================
    
    function getRowRange() {
        const selectedMode = document.querySelector('input[name="rangeMode"]:checked');
        const isAutoMode = selectedMode && selectedMode.value === 'auto';
        
        if (isAutoMode) {
            console.log('🔍 Используем автоопределение строк (по порядковому номеру 1)');
            return { start_row: null, end_row: null };
        }
        
        const startInput = document.getElementById('startRow');
        const endInput = document.getElementById('endRow');
        
        if (!startInput) {
            return { error: 'Поле "Начать со строки" не найдено' };
        }
        
        const startValue = startInput.value.trim();
        if (startValue === '') {
            startInput.style.borderColor = '#f44336';
            return { error: 'Укажите начальную строку' };
        }
        
        const start = parseInt(startValue);
        if (isNaN(start) || start < 1) {
            startInput.style.borderColor = '#f44336';
            return { error: 'Укажите корректную начальную строку (>= 1)' };
        }
        startInput.style.borderColor = '#dce3ec';
        
        let end = null;
        if (endInput) {
            const endValue = endInput.value.trim();
            if (endValue !== '') {
                end = parseInt(endValue);
                if (isNaN(end) || end < 1) {
                    endInput.style.borderColor = '#f44336';
                    return { error: 'Конечная строка должна быть >= 1' };
                }
                endInput.style.borderColor = '#dce3ec';
                
                if (start > end) {
                    startInput.style.borderColor = '#f44336';
                    endInput.style.borderColor = '#f44336';
                    return { error: 'Начальная строка не может быть больше конечной' };
                }
            }
        }
        
        console.log(`📋 Ручной режим: строки ${start} - ${end || 'конец'}`);
        return { start_row: start, end_row: end };
    }
    
    // ============================================
    // ОТПРАВКА ДАННЫХ С АНИМАЦИЕЙ ПРОГРЕССА (АСИНХРОННО)
    // ============================================
    
    if (fillBtn) {
        fillBtn.addEventListener('click', async function() {
            console.log('🔘 Кнопка "Заполнить ведомость" нажата');
            
            if (!selectedVK) {
                showNotification('❌ Выберите файл ВК', 'error');
                return;
            }
            
            if (!selectedProjects.length) {
                showNotification('❌ Выберите хотя бы один проект', 'error');
                return;
            }
            
            const range = getRowRange();
            if (range.error) {
                showNotification(`❌ ${range.error}`, 'error');
                return;
            }
            
            fillBtn.disabled = true;
            fillBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Заполнение...';
            
            showProgress();
            updateProgress(0, '🔄 Отправка запроса...', '⏳ Подготовка', Date.now());
            
            try {
                const requestData = {
                    file_id: selectedVK.id,
                    vk_file: selectedVK.name,
                    projects: selectedProjects.map(p => ({
                        id: p.id,
                        project: p.project
                    })),
                    start_row: range.start_row,
                    end_row: range.end_row
                };
                
                const response = await fetch('/statement/job_vk_async/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(requestData)
                });
                
                const data = await response.json();
                
                if (data.success && data.task_id) {
                    currentTaskId = data.task_id;
                    console.log('✅ Задача запущена, task_id:', currentTaskId);
                    
                    const startTime = Date.now();
                    const checkInterval = setInterval(async () => {
                        try {
                            const statusResponse = await fetch(`/statement/api/task/status/${currentTaskId}/`);
                            const statusData = await statusResponse.json();
                            
                            console.log('Статус задачи:', statusData.status);
                            
                            if (statusData.status === 'SUCCESS') {
                                clearInterval(checkInterval);
                                updateProgress(100, '✅ Обработка завершена!', 'Готово!', startTime);
                                setTimeout(() => {
                                    hideProgress();
                                    showResult(statusData.result);
                                    showNotification(`✅ Обработано строк: ${statusData.result.rows_processed || 0}`);
                                    fillBtn.disabled = false;
                                    fillBtn.innerHTML = '<span class="material-icons">auto_awesome</span> Заполнить ведомость';
                                }, 1000);
                                
                            } else if (statusData.status === 'FAILURE') {
                                clearInterval(checkInterval);
                                updateProgress(0, '❌ Ошибка обработки', statusData.error || 'Неизвестная ошибка', startTime);
                                setTimeout(() => {
                                    hideProgress();
                                    showNotification(`❌ ${statusData.error || 'Ошибка при обработке'}`, 'error');
                                    fillBtn.disabled = false;
                                    fillBtn.innerHTML = '<span class="material-icons">auto_awesome</span> Заполнить ведомость';
                                }, 2000);
                                
                            } else if (statusData.status === 'PROGRESS' && statusData.progress) {
                                const progress = statusData.progress;
                                const percent = progress.current || 0;
                                const statusText = progress.status || 'Обработка...';
                                const processed = progress.processed_rows || 0;
                                const total = progress.total_rows || 0;
                                
                                let statsText = `📊 Прогресс: ${percent}%`;
                                if (processed > 0) {
                                    statsText = `✅ Обработано: ${processed} из ${total || '?'}`;
                                }
                                
                                updateProgress(percent, statusText, statsText, startTime);
                                
                            } else if (statusData.status === 'PENDING') {
                                updateProgress(5, '⏳ Ожидание очереди...', 'Задача в очереди', startTime);
                            } else if (statusData.status === 'STARTED') {
                                updateProgress(10, '🔄 Начало обработки...', 'Запущено', startTime);
                            }
                            
                        } catch (err) {
                            console.error('Ошибка при опросе статуса:', err);
                        }
                    }, 1500);
                    
                    window._currentInterval = checkInterval;
                    
                } else {
                    throw new Error(data.error || 'Не удалось запустить обработку');
                }
                
            } catch (error) {
                console.error('❌ Ошибка:', error);
                updateProgress(0, '❌ Ошибка', error.message, Date.now());
                setTimeout(() => {
                    hideProgress();
                    showNotification(`❌ ${error.message}`, 'error');
                    fillBtn.disabled = false;
                    fillBtn.innerHTML = '<span class="material-icons">auto_awesome</span> Заполнить ведомость';
                }, 2000);
            }
        });
    }
    
    function showResult(result) {
        if (!resultContainer) return;
        
        resultContainer.innerHTML = '';
        resultContainer.style.display = 'flex';
        resultContainer.style.flexDirection = 'column';
        resultContainer.style.alignItems = 'flex-start';
        
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
            ${selectedVK.config ? `<br>📁 Конфигурация: ${selectedVK.config.name}` : ''}
            ${selectedVK.relative_path ? `<br>📂 Папка: ${selectedVK.relative_path}` : ''}
        `;
        resultContainer.appendChild(fileInfo);
        
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
            <span>📄 Диапазон: <strong>${result.row_range || 'автоопределение'}</strong></span>
        `;
        resultContainer.appendChild(infoLine);
        
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
        
        if (result.config_used) {
            const configInfo = document.createElement('div');
            configInfo.style.cssText = `
                font-size: 0.75rem;
                color: #888;
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid #e0e7f0;
            `;
            configInfo.innerHTML = `🔧 Конфигурация: ${result.config_used.name}`;
            resultContainer.appendChild(configInfo);
        }
    }
    
    // Обработчик отмены обработки файла
    if (cancelBtn) {
        cancelBtn.addEventListener('click', async () => {
            if (currentTaskId) {
                try {
                    const response = await fetch(`/statement/api/task/cancel/${currentTaskId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                    const data = await response.json();
                    if (data.success) {
                        if (window._currentInterval) {
                            clearInterval(window._currentInterval);
                        }
                        showNotification('⚠️ Обработка отменена', 'info');
                        hideProgress();
                        fillBtn.disabled = false;
                        fillBtn.innerHTML = '<span class="material-icons">auto_awesome</span> Заполнить ведомость';
                    }
                } catch (error) {
                    console.error('Ошибка отмены:', error);
                }
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
            max-height: 350px;
            overflow-y: auto;
            min-width: 350px;
            width: 100%;
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
        button:disabled {
            cursor: not-allowed;
            opacity: 0.6;
        }
        input[type="radio"] {
            cursor: pointer;
        }
        label {
            cursor: pointer;
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // ИНИЦИАЛИЗАЦИЯ ПОЛЕЙ ВВОДА И РЕЖИМА
    // ============================================
    
    const defaultStartRow = document.getElementById('startRow');
    const defaultEndRow = document.getElementById('endRow');
    if (defaultStartRow) defaultStartRow.value = '11';
    if (defaultEndRow) defaultEndRow.value = '50';
    
    const autoRadioInitial = document.querySelector('input[name="rangeMode"][value="auto"]');
    if (autoRadioInitial) {
        autoRadioInitial.checked = true;
        const manualInputsElem = document.getElementById('manualRangeInputs');
        const autoInfoElem = document.getElementById('autoRangeInfo');
        if (manualInputsElem) manualInputsElem.style.display = 'none';
        if (autoInfoElem) autoInfoElem.style.display = 'flex';
        console.log('✅ Авторежим включен по умолчанию');
    }
    
    // ============================================
    // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
    // ============================================
    
    loadIndexedFiles('');
    loadProjects();
    
    setInterval(() => {
        loadIndexStats();
    }, 30000);
});