class ArchiveApp {
    constructor() {
        this.baseUrl = ARCHIVE_API_URL;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadArchive();
    }
    
    bindEvents() {
        // Search
        document.getElementById('archiveSearch').addEventListener('input', (e) => {
            this.searchArchive(e.target.value);
        });
        
        // Refresh
        document.getElementById('refreshArchive').addEventListener('click', () => {
            this.loadArchive();
        });
    }
    
    async loadArchive() {
        try {
            const response = await fetch(this.baseUrl);
            if (response.ok) {
                const positions = await response.json();
                this.renderArchive(positions);
            }
        } catch (error) {
            console.error('Error loading archive:', error);
        }
    }
    
    async searchArchive(query) {
        if (!query) {
            this.loadArchive();
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}search/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                },
                body: JSON.stringify({ query })
            });
            
            if (response.ok) {
                const results = await response.json();
                this.renderArchive(results);
            }
        } catch (error) {
            console.error('Error searching archive:', error);
        }
    }
    
    renderArchive(positions) {
        const tbody = document.querySelector('#archiveTable tbody');
        tbody.innerHTML = '';
        
        positions.forEach(pos => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${pos.id}</td>
                <td>${pos.article}</td>
                <td>${pos.party}</td>
                <td>${pos.address}</td>
                <td>${pos.delete_reason || 'Не указана'}</td>
                <td>${new Date(pos.deleted_at).toLocaleString()}</td>
                <td>${pos.deleted_by || 'Система'}</td>
                <td>
                    <button class="btn btn-sm restore-btn" data-id="${pos.id}">
                        <i class="fas fa-undo"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Initialize archive app
document.addEventListener('DOMContentLoaded', () => {
    new ArchiveApp();
});