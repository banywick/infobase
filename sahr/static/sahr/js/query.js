// scripts.js

// Функция для получения CSRF-токена из мета-тега
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// Обработчик отправки формы поиска
document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Предотвращаем отправку формы

    const query = document.querySelector('input[name="query"]').value;
    const csrfToken = getCSRFToken();

    fetch('/sahr/sahr_find/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Отправляем CSRF-токен в заголовке
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Здесь вы можете обработать ответ от сервера
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

// Обработчик ввода в поле артикула
const check_article = document.getElementById('article');
const views_title = document.getElementById('title');
const selectElement = document.getElementById('party');
const hidden_id = document.createElement('input'); // Если нужен скрытый инпут для ID
const base_unit = document.createElement('input'); // Если нужен скрытый инпут для base_unit
hidden_id.type = 'hidden';
hidden_id.name = 'id';
base_unit.type = 'hidden';
base_unit.name = 'base_unit';
document.getElementById('articleForm').appendChild(hidden_id);
document.getElementById('articleForm').appendChild(base_unit);

check_article.addEventListener('input', async function () {
    const enteredArticle = check_article.value;
    console.log(enteredArticle);

    try {
        if (enteredArticle.trim() === '') {
            // Если в инпуте нет значений, очищаем название
            views_title.value = '';
            selectElement.innerHTML = '';
        } else {
            const response = await fetch(`/sahr/check-article_form/${enteredArticle}/`);
            const data = await response.json();
            console.log(data);

            selectElement.innerHTML = '';
            for (let i in data.party) {
                const option = document.createElement('option');
                option.value = data.party[i];
                option.text = data.party[i];
                selectElement.appendChild(option);
            }
            // Отображаем название рядом с инпутом
            if (data.title) {
                views_title.value = data.title;
                hidden_id.value = data.id;
            }
            if (data.base_unit) {
                base_unit.value = data.base_unit;
            }
            if (data.error) {
                views_title.value = data.error;
            }
        }
    } catch (error) {
        console.error('Ошибка при выполнении fetch-запроса:', error);
    }
});

// Функция для отправки формы артикула
function submitArticleForm() {
    const formData = new FormData(document.getElementById('articleForm'));
    const csrfToken = getCSRFToken();
    fetch('/sahr/add_position/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken // Отправляем CSRF-токен в заголовке
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}
