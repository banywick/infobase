// Dashboard logic
class Dashboard {
    constructor() {
        this.chart = null;
        this.init();
    }
    
    async init() {
        await this.loadStats();
        await this.loadExpiringEmployees();
    }
    
    async loadStats() {
        try {
            const stats = await API.getDashboardStats();
            
            document.getElementById('totalEmployees').textContent = stats.total_employees || 0;
            document.getElementById('totalWorkwear').textContent = stats.total_workwear || 0;
            document.getElementById('expiringItems').textContent = stats.expiring_items || 0;
            document.getElementById('expiredItems').textContent = stats.expired_items || 0;
            
            this.createChart(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    createChart(stats) {
        const ctx = document.getElementById('statusChart').getContext('2d');
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Активные', 'Истекает срок', 'Просрочены'],
                datasets: [{
                    data: [
                        stats.total_workwear - stats.expiring_items - stats.expired_items,
                        stats.expiring_items || 0,
                        stats.expired_items || 0
                    ],
                    backgroundColor: ['#27ae60', '#f39c12', '#e74c3c'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadExpiringEmployees() {
        try {
            const items = await API.getExpiringItems();
            
            const container = document.getElementById('expiringEmployeesList');
            
            if (items.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-success py-3">
                        <i class="fas fa-check-circle"></i> Все сотрудники в порядке
                    </div>
                `;
                return;
            }
            
            // Группировка по сотрудникам
            const employees = {};
            items.forEach(item => {
                if (!employees[item.employee]) {
                    employees[item.employee] = {
                        id: item.employee,
                        name: item.employee_name,
                        items: []
                    };
                }
                employees[item.employee].items.push(item);
            });
            
            let html = '<div class="list-group">';
            Object.values(employees).forEach(emp => {
                const days = Math.min(...emp.items.map(i => i.days_until_expiration));
                const statusClass = days <= 7 ? 'danger' : days <= 15 ? 'warning' : 'info';
                
                html += `
                    <a href="/workwear/employees/${emp.id}/" class="list-group-item list-group-item-action">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${emp.name}</strong>
                                <span class="badge bg-${statusClass} ms-2">${emp.items.length} предметов</span>
                            </div>
                            <div>
                                <span class="text-${statusClass}">
                                    <i class="fas fa-clock"></i> ${days} дней
                                </span>
                            </div>
                        </div>
                        <div class="mt-1">
                            ${emp.items.map(item => `
                                <span class="badge bg-light text-dark me-1">
                                    ${item.name} (до ${item.expiration_date})
                                </span>
                            `).join('')}
                        </div>
                    </a>
                `;
            });
            html += '</div>';
            
            container.innerHTML = html;
        } catch (error) {
            console.error('Error loading expiring employees:', error);
        }
    }
}

// Инициализация дашборда
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});