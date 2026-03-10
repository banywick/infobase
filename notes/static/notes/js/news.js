async function loadNews() {
    const response = await fetch("/reviews/news/");
    const newsItems = await response.json();
    const container = document.querySelector(".list_new_function");

    container.innerHTML = ""; // Очищаем блок перед загрузкой новых данных

    newsItems.forEach(item => {
        const date = new Date(item.created_at);
        const formattedDate = `${date.getDate().toString().padStart(2, '0')}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getFullYear()}`;

        container.innerHTML += `
            <div class="news_item">
                <div class="news_date">${formattedDate}</div>
                <h3>${item.title}</h3>
                <p>${item.description}</p>
                ${item.link ? `<a href="${item.link}" class="news_link">Перейти →</a>` : ""}
            </div>
        `;
    });
}

// Добавляем обработчик клика на кнопку "#whats_button"
document.getElementById("whats_button").addEventListener("click", function() {
    loadNews(); // Загружаем новости при клике на кнопку
});