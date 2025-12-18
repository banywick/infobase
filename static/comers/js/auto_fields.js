const check_party = document.querySelector('.check_party');
const views_title = document.querySelector('.views_title');
const views_article = document.getElementById('hidden_article');
const views_unit = document.getElementById('hidden_unit');
const views_project = document.getElementById('hidden_project');
const views_quantity = document.getElementById('hidden_quantity');
const views_party = document.getElementById('hidden_party');


check_party.addEventListener('input', async function () {
    const enteredParty = check_party.value.trim(); 
    
    try {
        if (enteredParty === '') {
            // Если в инпуте нет значений, очищаем все поля
            views_title.value = '';
            views_article.value = '';
            views_unit.value = '';
            views_project.value = '';
            views_quantity.value = '';
            views_party.value = '';
        } else {
            const response = await fetch(`/comers/get_party_info/${enteredParty}/`);
            
            // Сначала проверяем статус ответа
            console.log('Статус ответа:', response.status);
            
            if (response.status === 404) {
                // Партия не найдена
                const errorData = await response.json();
                console.log('Ошибка:', errorData);
                views_title.value = errorData.error || 'Партия не найдена';
                views_title.style.color = 'red';
                
                // Очищаем остальные поля
                views_article.value = '';
                views_unit.value = '';
                views_project.value = '';
                views_quantity.value = '';
                views_party.value = '';
                
            } else if (response.ok) {
                // Партия найдена
                const data = await response.json();
                console.log('Успешный ответ:', data);
                
                // В зависимости от структуры ответа
                if (data.type === "exact" && data.data) {
                    views_title.value = data.data.title;
                    views_title.style.color = '';
                    
                    if (views_article) views_article.value = data.data.article || '';
                    if (views_unit) views_unit.value = data.data.base_unit || '';
                    if (views_project) views_project.value = data.data.project || '';
                    if (views_quantity) views_quantity.value = data.data.quantity || '';
                    if (views_party) views_party.value = data.data.party || '';
                    
                } else if (data.title) {
                    // Альтернативная структура (как в старом коде)
                    views_title.value = data.title;
                    views_title.style.color = '';
                    
                    if (views_article) views_article.value = data.article || '';
                    if (views_unit) views_unit.value = data.base_unit || '';
                    if (views_project) views_project.value = data.project || '';
                    if (views_quantity) views_quantity.value = data.quantity || '';
                    if (views_party) views_party.value = data.party || '';
                }
            }
        }
    } catch (error) {
        console.error('Ошибка при выполнении fetch-запроса:', error);
        views_title.value = 'Партия не найдена';
        views_title.style.color = 'red';
    }
});