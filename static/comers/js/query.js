// Open popup

function openPopup(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

// Close popup
function closePopup(modalId) {
    if (modalId) {
        document.getElementById(modalId).style.display = 'none';
    } else {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
    document.getElementById('overlay').style.display = 'none';
}

// Add supplier
function addSupplier(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const supplierName = formData.get('supplierName');
    console.log('Добавлен поставщик:', supplierName);
    // Here you would typically send data to the server
    closePopup('addSupplierModal');
}

// Add data
function addData(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => data[key] = value);
    console.log('Добавлены данные:', data);
    // Here you would typically send data to the server
    closePopup('addDataModal');
}

// Apply filters
function applyFilters() {
    const supplier = document.getElementById('supplierFilter').value;
    const leading = document.getElementById('leadingFilter').value;
    const status = document.getElementById('statusFilter').value;
    console.log('Применены фильтры:', { supplier, leading, status });
    // Here you would typically send filter data to the server
}

// Clear filters
function clearFilters() {
    document.getElementById('supplierFilter').selectedIndex = 0;
    document.getElementById('leadingFilter').selectedIndex = 0;
    document.getElementById('statusFilter').selectedIndex = 0;
    console.log('Фильтры сброшены');
    // Here you would typically clear filter data on the server
}

// Load data into the table
function loadData() {
    // Example data
    const data = [
        {
            invoiceNumber: '2430606',
            date: '1 сентября 2023 г.',
            supplier: 'ЗАО профессиональные профессионалы',
            article: 'B00021069',
            name: 'Шайба 4,3 DIN 433 A2',
            unit: 'шт.',
            quantity: '1000',
            comment: 'недовоз',
            description: '11 гаек, 1 фитинг',
            specialist: 'Петров П.П.',
            leading: 'Иванов И.И.',
            status: '<span class="status status-delivered">депестовка</span>',
            note: 'Поставщик до поставить данную продукцию не сможет.'
        },
        {
            invoiceNumber: '2430606',
            date: '1 сентября 2023 г.',
            supplier: 'ЗАО профессиональные профессионалы',
            article: 'B00021069',
            name: 'Шайба 4,3 DIN 433 A2',
            unit: 'шт.',
            quantity: '1000',
            comment: 'брак',
            description: 'Пробита тара, вытекло 350 г',
            specialist: 'Петров П.П.',
            leading: 'Иванов И.И.',
            status: '<span class="status status-processed">обработка</span>',
            note: 'Поставщик до поставить данную продукцию не сможет.'
        }
    ];

    const tableBody = document.getElementById('invoiceTableBody');
    tableBody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.invoiceNumber}</td>
            <td>${item.date}</td>
            <td>${item.supplier}</td>
            <td>${item.article}</td>
            <td>${item.name}</td>
            <td>${item.unit}</td>
            <td>${item.quantity}</td>
            <td>${item.comment}</td>
            <td>${item.description}</td>
            <td>${item.specialist}</td>
            <td>${item.leading}</td>
            <td>${item.status}</td>
            <td>${item.note}</td>
            <td class="action-buttons">
                <button>редактировать</button>
                <button class="status-btn">статус</button>
                <button class="delete">удалить</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Load data on page load
window.onload = loadData;


