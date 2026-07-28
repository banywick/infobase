// Главное приложение
class App {
    constructor() {
        this.init();
    }
    
    init() {
        // Активируем всплывающие подсказки
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Активируем уведомления
        this.setupNotifications();
    }
    
    setupNotifications() {
        // Автоматическое скрытие уведомлений
        document.querySelectorAll('.alert-dismissible').forEach(alert => {
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        });
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});