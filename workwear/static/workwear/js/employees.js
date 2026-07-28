// Employees page logic
class EmployeesPage {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {
            search: '',
            department: '',
            status: ''
        };
        this.employees = [];
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadEmployees();
    }
    
    bindEvents() {
        // Поиск с debounce
        let searchTimeout;
        document.getElementById('searchInput').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.currentPage = 1;
                this.loadEmployees();
            }, 300);
        });
        
        document.getElementById('departmentFilter').addEventListener('input', (e) => {
            this.filters.department = e.target.value;
            this.currentPage = 1;
            this.loadEmployees();
        });
        
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.currentPage = 1;
            this.loadEmployees();
        });
        
        document.getElementById('resetFilters').addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            document.getElementById('departmentFilter').value = '';
            document.getElementById('statusFilter').value = '';
            this.filters = { search: '', department: '', status: '' };
            this.currentPage = 1;
            this.loadEmployees();
        });
        
        document.getElementById('saveEmployeeBtn').addEventListener('click', () => {
            this.saveEmployee();
        });
    }
    
    async loadEmployees() {
        try {
            const container = document.getElementById('employeesContainer');
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Загрузка...</span>
                    </div>
                    <p class="mt-2 text-muted">Загрузка сотрудников...</p>
                </div>
            `;
            
            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.filters
            };
            
            // Удаляем пустые параметры
            Object.keys(params).forEach(key => {
                if (!params[key]) delete params[key];
            });
            
            const response = await API.getEmployees(params);
            
            this.employees = response.results || [];
            this.renderEmployees(this.employees);
            this.renderPagination(response);
            
        } catch (error) {
            console.error('Error loading employees:', error);
            document.getElementById('employeesContainer').innerHTML = `
                <div class="col-12 text-center py-5 text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                    <p class="mt-2">Ошибка загрузки сотрудников</p>
                </div>
            `;
        }
    }
    
    renderEmployees(employees) {
        const container = document.getElementById('employeesContainer');
        
        if (employees.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5 text-muted">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <p>Сотрудники не найдены</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        employees.forEach(emp => {
            // Определяем статус
            let statusClass = 'status-ok';
            let statusText = 'В порядке';
            
            if (emp.expired_count > 0) {
                statusClass = 'status-expired';
                statusText = 'Просрочено';
            } else if (emp.expiring_count > 0) {
                statusClass = 'status-expiring';
                statusText = 'Истекает срок';
            }
            
            html += `
                <div class="col-lg-3 col-md-4 col-sm-6">
                    <div class="employee-card card ${statusClass} fade-in" 
                         onclick="window.location.href='/workwear/employees/${emp.id}/'">
                        <div class="card-body">
                            ${emp.photo ? 
                                `<img src="${emp.photo}" class="card-img-top" alt="${emp.full_name}">` :
                                `<div class="card-img-top d-flex align-items-center justify-content-center bg-light rounded-circle mx-auto" 
                                     style="width:100px;height:100px;font-size:3rem;color:#6c757d;">
                                    <i class="fas fa-user"></i>
                                </div>`
                            }
                            <h5 class="employee-name">${emp.full_name}</h5>
                            <div class="employee-department">${emp.department}</div>
                            <div class="employee-position">${emp.position}</div>
                            <div class="mt-2">
                                <span class="status-badge ${statusClass}">
                                    ${statusText}
                                </span>
                                ${emp.expiring_count > 0 ? 
                                    `<span class="badge bg-warning text-dark ms-1">${emp.expiring_count}</span>` : ''}
                                ${emp.expired_count > 0 ? 
                                    `<span class="badge bg-danger ms-1">${emp.expired_count}</span>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
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
        
        // Previous
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage - 1}">«</a>
        </li>`;
        
        // Pages
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else if (i <= 3 || i > totalPages - 3 || Math.abs(i - this.currentPage) <= 1) {
                html += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
            } else if (i === 4 && this.currentPage > 5) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            } else if (i === totalPages - 3 && this.currentPage < totalPages - 4) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        // Next
        html += `<li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${this.currentPage + 1}">»</a>
        </li>`;
        
        html += '</ul></nav>';
        container.innerHTML = html;
        
        // Обработчики кликов
        container.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page > 0 && page <= totalPages && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadEmployees();
                }
            });
        });
    }
    
    async saveEmployee() {
        const form = document.getElementById('addEmployeeForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            document.getElementById('saveEmployeeBtn').disabled = true;
            document.getElementById('saveEmployeeBtn').innerHTML = 
                '<span class="spinner-border spinner-border-sm"></span> Сохранение...';
            
            await API.createEmployee(data);
            
            // Закрываем модалку
            const modal = bootstrap.Modal.getInstance(document.getElementById('addEmployeeModal'));
            modal.hide();
            
            // Перезагружаем список
            this.currentPage = 1;
            this.loadEmployees();
            
            // Показываем уведомление
            this.showNotification('Сотрудник успешно добавлен', 'success');
            
        } catch (error) {
            console.error('Error saving employee:', error);
            this.showNotification('Ошибка при добавлении сотрудника', 'danger');
        } finally {
            document.getElementById('saveEmployeeBtn').disabled = false;
            document.getElementById('saveEmployeeBtn').innerHTML = 'Сохранить';
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
document.addEventListener('DOMContentLoaded', () => {
    new EmployeesPage();
});