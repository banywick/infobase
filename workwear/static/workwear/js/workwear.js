// Workwear page logic
class WorkwearPage {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 50;
        this.filters = {
            search: '',
            status: '',
            category: '',
            expiration_from: '',
            expiration_to: ''
        };
        this.categories = [];
        this.init();
    }
    
    async init() {
        this.bindEvents();
        await this.loadCategories();
        await this.loadEmployees();
        await this.loadWorkwear();
    }
    
    bindEvents() {
        let searchTimeout;
        document.getElementById('searchInput').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.currentPage = 1;
                this.loadWorkwear();
            }, 300);
        });
        
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('expirationFrom').addEventListener('change', (e) => {
            this.filters.expiration_from = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('expirationTo').addEventListener('change', (e) => {
            this.filters.expiration_to = e.target.value;
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('resetFilters').addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            document.getElementById('statusFilter').value = '';
            document.getElementById('categoryFilter').value = '';
            document.getElementById('expirationFrom').value = '';
            document.getElementById('expirationTo').value = '';
            this.filters = { search: '', status: '', category: '', expiration_from: '', expiration_to: '' };
            this.currentPage = 1;
            this.loadWorkwear();
        });
        
        document.getElementById('saveWorkwearBtn').addEventListener('click', () => {
            this.saveWorkwear();
        });
    }
    
    async loadCategories() {
        try {
            const categories = await API.getCategories();
            this.categories = categories;
            
            // Заполняем фильтр категорий
            const filterSelect = document.getElementById('categoryFilter');
            const formSelect = document.getElementById('categorySelect');
            
            categories.forEach(cat => {
                if (cat.is_active) {
                    const opt1 = document.createElement('option');
                    opt1.value = cat.id;
                    opt1.textContent = cat.name;
                    filterSelect.appendChild(opt1);
                    
                    const opt2 = document.createElement('option');
                    opt2.value = cat.id;
                    opt2.textContent = cat.name;
                    formSelect.appendChild(opt2);
                }
            });
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }
    
    async loadEmployees() {
        try {
            const response = await API.getEmployees({ page_size: 1000 });
            const select = document.getElementById('employeeSelect');
            
            (response.results || []).forEach(emp => {
                const opt = document.createElement('option');
                opt.value = emp.id;
                opt.textContent = emp.full_name;
                select.appendChild(opt);
            });
        } catch (error) {
            console.error('Error loading employees:', error);
        }
    }
    
    async loadWorkwear() {
        try {
            const container = document.getElementById('workwearTableBody');
            
            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.filters
            };
            
            Object.keys(params).forEach(key => {
                if (!params[key]) delete params[key];
            });
            
            const response = await API.getWorkwearItems(params);
            this.renderWorkwear(response.results || []);
            this.renderPagination(response);
            
        } catch (error) {
            console.error('Error loading workwear:', error);
            document.getElementById('workwearTableBody').innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-3 text-danger">
                        <i class="fas fa-exclamation-triangle"></i> Ошибка загрузки данных
                    </td>
                </tr>
            `;
        }
    }
    
    renderWorkwear(items) {
        const container = document.getElementById('workwearTableBody');
        
        if (items.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-3 text-muted">
                        <i class="fas fa-tshirt fa-2x d-block mb-2"></i>
                        Спецодежда не найдена
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        items.forEach(item => {
            const statusMap = {
                'active': { class: 'status-active', text: 'Активна' },
                'expiring': { class: 'status-expiring', text: 'Истекает' },
                'expired': { class: 'status-expired', text: 'Просрочена' }
            };
            const status = statusMap[item.status] || statusMap.active;
            
            const days = item.days_until_expiration || 0;
            const daysColor = days <= 7 ? 'text-danger' : days <= 15 ? 'text-warning' : 'text-success';
            
            html += `
                <tr class="${item.status === 'expired' ? 'table-danger' : item.status === 'expiring' ? 'table-warning' : ''}">
                    <td>
                        <a href="/workwear/employees/${item.employee}/" class="text-decoration-none">
                            ${item.employee_name}
                        </a>
                    </td>
                    <td><strong>${item.name}</strong></td>
                    <td>${item.category_name}</td>
                    <td>${item.size || '-'}</td>
                    <td>${item.issue_date}</td>
                    <td>${item.expiration_date}</td>
                    <td>
                        <span class="status-badge ${status.class}">
                            ${status.text}
                        </span>
                    </td>
                    <td class="${daysColor}">
                        ${days > 0 ? `${days} дн.` : '-'}
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="workwearPage.editItem(${item.id})" title="Редактировать">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-success" onclick="workwearPage.returnItem(${item.id})" title="Вернуть">
                                <i class="fas fa-undo"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="workwearPage.deleteItem(${item.id})" title="Списать">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        container.innerHTML = html;
    }
    
    renderPagination(data) {
        const container = document.getElementById('paginationContainer');
        
        if (!data || data.count <= this.pageSize) {
            container.innerHTML = '';
            return;
        }
        
        const totalPages = Math.ceil(data.count / this.pageSize);
        let html = '<nav><ul class="pagination">';
        
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage - 1}">«</a>
        </li>`;
        
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === this.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        
        html += `<li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage + 1}">»</a>
        </li>`;
        
        html += '</ul></nav>';
        container.innerHTML = html;
        
        container.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page > 0 && page <= totalPages && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadWorkwear();
                }
            });
        });
    }
    
    async saveWorkwear() {
        const form = document.getElementById('addWorkwearForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            document.getElementById('saveWorkwearBtn').disabled = true;
            document.getElementById('saveWorkwearBtn').innerHTML = 
                '<span class="spinner-border spinner-border-sm"></span> Сохранение...';
            
            await API.createWorkwearItem(data);
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('addWorkwearModal'));
            modal.hide();
            
            this.currentPage = 1;
            this.loadWorkwear();
            this.showNotification('Спецодежда успешно добавлена', 'success');
            
        } catch (error) {
            console.error('Error saving workwear:', error);
            this.showNotification('Ошибка при добавлении спецодежды', 'danger');
        } finally {
            document.getElementById('saveWorkwearBtn').disabled = false;
            document.getElementById('saveWorkwearBtn').innerHTML = 'Сохранить';
        }
    }
    
    async returnItem(id) {
        if (!confirm('Вы уверены, что хотите вернуть эту спецодежду?')) return;
        
        try {
            await API.returnWorkwearItem(id);
            this.loadWorkwear();
            this.showNotification('Спецодежда возвращена', 'success');
        } catch (error) {
            console.error('Error returning workwear:', error);
            this.showNotification('Ошибка при возврате спецодежды', 'danger');
        }
    }
    
    async deleteItem(id) {
        if (!confirm('Вы уверены, что хотите списать эту спецодежду?')) return;
        
        try {
            await API.deleteWorkwearItem(id);
            this.loadWorkwear();
            this.showNotification('Спецодежда списана', 'success');
        } catch (error) {
            console.error('Error deleting workwear:', error);
            this.showNotification('Ошибка при списании спецодежды', 'danger');
        }
    }
    
    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 5000);
    }
}

// Инициализация
let workwearPage;
document.addEventListener('DOMContentLoaded', () => {
    workwearPage = new WorkwearPage();
});