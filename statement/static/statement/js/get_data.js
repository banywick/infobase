(function() {
    // --- мок данные: варианты ВК
    const vkMockList = [
        'ВК-24-101 (Жилой комплекс)',
        'ВК-24-102 (Паркинг)',
        'ВК-СМ-9 (Офисный центр)',
        'ВК-ТР-5 (Торговый ряд)',
        'ВК-ОЗ-12 (Озеленение)',
        'ВК-Э-7 (Эстакада)',
        'ВК-ПС-3 (Подземные сети)',
        'ВК-М-22 (Магистраль)'
    ];

    // --- мок данные: проекты (для мультиселекта)
    const projectsMockList = [
        'Проект Альфа (жилой дом)',
        'Проект Бета (благоустройство)',
        'Проект Гамма (квартал Сити)',
        'Проект Дельта (инфраструктура)',
        'Проект Эпсилон (набережная)',
        'Проект Зета (парк)',
        'Проект Эта (логистика)',
        'Проект Каппа (теплотрасса)'
    ];

    // DOM elements
    const vkInput = document.getElementById('vkSearchInput');
    const vkSuggest = document.getElementById('vkSuggestList');
    const selectedChip = document.getElementById('selectedVKChip');
    const selectedVKNameSpan = document.getElementById('selectedVKName');
    const projectsPanel = document.getElementById('projectsPanel');
    const fillBtn = document.getElementById('fillBtn');
    const resultContainer = document.getElementById('resultLinkContainer');
    const excelLink = document.getElementById('excelLink');

    // мультиселект проекты
    const projectSearchInput = document.getElementById('projectSearchInput');
    const projectSuggestList = document.getElementById('projectSuggestList');
    const multiselectContainer = document.getElementById('multiselectContainer');

    // Состояния
    let selectedVK = null;                      // выбранный ВК (строка)
    let selectedProjects = [];                   // массив выбранных проектов (строки)
    let filteredProjects = [...projectsMockList]; // текущий фильтр для выпадающего списка

    // --- helpers: скрыть все дропдауны
    function hideAllDropdowns() {
        vkSuggest.style.display = 'none';
        projectSuggestList.style.display = 'none';
    }

    // --- обновить отображение выбранных проектов (чипы внутри мультиселекта)
    function renderSelectedProjects() {
        // очистим контейнер, но оставим input
        const inputEl = projectSearchInput;
        multiselectContainer.innerHTML = ''; 
        // добавить chip'ы для каждого выбранного проекта
        selectedProjects.forEach(proj => {
            const chip = document.createElement('span');
            chip.className = 'selected-project-tag';
            chip.innerHTML = `${proj} <span class="material-icons" data-remove-project="${proj}">close</span>`;
            multiselectContainer.appendChild(chip);
        });
        // добавить обратно input
        multiselectContainer.appendChild(inputEl);
        // навесить обработчики на кнопки удаления
        document.querySelectorAll('[data-remove-project]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectToRemove = btn.getAttribute('data-remove-project');
                selectedProjects = selectedProjects.filter(p => p !== projectToRemove);
                renderSelectedProjects(); 
                filterProjectList(); // обновить выпадающий список
                updateFillButtonState();
                e.stopPropagation();
            });
        });
        // подрегулировать отображение плейсхолдера
        inputEl.placeholder = selectedProjects.length ? '' : 'Введите название проекта...';
    }

    // --- фильтрация проектов на основе ввода и исключение уже выбранных
    function filterProjectList() {
        const searchTerm = projectSearchInput.value.toLowerCase();
        // из исходного списка исключаем выбранные, и фильтруем по вводу
        filteredProjects = projectsMockList.filter(p => 
            !selectedProjects.includes(p) && p.toLowerCase().includes(searchTerm)
        );
        renderProjectSuggestions();
    }

    // --- отобразить подсказки проектов
    function renderProjectSuggestions() {
        projectSuggestList.innerHTML = '';
        if (filteredProjects.length === 0) {
            projectSuggestList.style.display = 'none';
            return;
        }
        filteredProjects.forEach(proj => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="material-icons">folder</span>${proj}`;
            li.addEventListener('click', () => {
                // добавить проект, если ещё не выбран
                if (!selectedProjects.includes(proj)) {
                    selectedProjects.push(proj);
                    renderSelectedProjects();
                    projectSearchInput.value = '';  // очистить поиск
                    filterProjectList();            // обновить список, исключив выбранные
                    updateFillButtonState();
                }
                projectSuggestList.style.display = 'none';
            });
            projectSuggestList.appendChild(li);
        });
        projectSuggestList.style.display = 'block';
    }

    // --- управление кнопкой "Заполнить ведомость"
    function updateFillButtonState() {
        if (selectedVK && selectedProjects.length > 0) {
            fillBtn.disabled = false;
        } else {
            fillBtn.disabled = true;
        }
    }

    // --- сброс состояния проектов при смене ВК (можно оставить старую логику, но чистим)
    function resetProjectsAndLink() {
        selectedProjects = [];
        renderSelectedProjects();
        projectSearchInput.value = '';
        filterProjectList();
        resultContainer.style.display = 'none';
        updateFillButtonState();
    }

    // --- обработчики поиска ВК (живой поиск)
    vkInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length === 0) {
            vkSuggest.style.display = 'none';
            return;
        }
        const filtered = vkMockList.filter(vk => vk.toLowerCase().includes(query));
        vkSuggest.innerHTML = '';
        if (filtered.length === 0) {
            vkSuggest.style.display = 'none';
            return;
        }
        filtered.forEach(vk => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="material-icons">feed</span>${vk}`;
            li.addEventListener('click', () => {
                // выбираем ВК
                selectedVK = vk;
                selectedVKNameSpan.textContent = vk;
                selectedChip.style.display = 'inline-flex';
                vkInput.value = ''; // можно очистить поле
                vkSuggest.style.display = 'none';
                // показываем панель проектов
                projectsPanel.classList.add('visible');
                // сбрасываем проекты и ссылку
                resetProjectsAndLink();
            });
            vkSuggest.appendChild(li);
        });
        vkSuggest.style.display = 'block';
    });

    // скрыть выпадающий список ВК при клике вне
    document.addEventListener('click', function(e) {
        if (!vkInput.contains(e.target) && !vkSuggest.contains(e.target)) {
            vkSuggest.style.display = 'none';
        }
        if (!multiselectContainer.contains(e.target) && !projectSuggestList.contains(e.target)) {
            projectSuggestList.style.display = 'none';
        }
    });

    // --- работа с поиском проектов
    projectSearchInput.addEventListener('input', filterProjectList);

    // при фокусе на поле проектов показываем список, если есть что показать
    projectSearchInput.addEventListener('focus', () => {
        filterProjectList(); // обновить фильтр с учётом исключённых
        if (filteredProjects.length > 0) {
            projectSuggestList.style.display = 'block';
        }
    });

    // запрещаем скрытие при клике внутри списка
    projectSuggestList.addEventListener('click', (e) => e.stopPropagation());

    // --- кнопка "Заполнить ведомость"
    fillBtn.addEventListener('click', function() {
        // симулируем успешное заполнение и создаём ссылку на сетевой Excel
        // генерируем случайный путь (в реальности здесь был бы fetch)
        const timestamp = Date.now();
        const fakeNetworkPath = `\\\\server\\excel_reports\\ВК_${selectedVK.replace(/[^a-zA-Z0-9-]/g,'_')}_${timestamp}.xlsx`;
        // также можно преобразовать в файловую ссылку file:// (но браузеры блокируют, используем file:// или unc)
        // для демонстрации используем file:// + заменим слэши
        const networkLink = `file://${fakeNetworkPath.replace(/\\/g,'/')}`;
        excelLink.href = networkLink;
        excelLink.textContent = fakeNetworkPath; // покажем UNC путь
        resultContainer.style.display = 'flex';

        // можно показать сообщение (опционально)
        setTimeout(() => {
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 50);
    });

    // инициализация: рендер чипов проектов (пусто)
    renderSelectedProjects();
    filterProjectList(); // начальный список проектов (все, кроме выбранных, но их нет)

    // доп. если кликнули на крестик уже выбранного ВК (можно добавить)
    // но по задаче после клика по варианту открывается доп.поле — уже работает

    // для красоты: скрывать дропдаун при потере фокуса
    window.addEventListener('click', function(e) {
        if (!e.target.closest('.multiselect-relative')) {
            projectSuggestList.style.display = 'none';
        }
    });

    // также обработка удаления выбранного ВК (по желанию не требуется, но можно скрыть)
    // в текущем дизайне не предусмотрено, но можно через крестик позже
})();