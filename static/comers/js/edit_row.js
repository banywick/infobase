// Более надежный вариант с делегированием событий
function setupEditHandlers() {
    // Обработчик для всей страницы
    document.addEventListener('click', function(e) {
        // Проверяем разные возможные места клика:
        
        // 1. Клик по самому контейнеру
        if (e.target.classList.contains('edit_invoice_button') || 
            e.target.classList.contains('edit_button')) {
            handleEditClick(e.target);
            return;
        }
        
        // 2. Клик по картинке внутри
        if (e.target.tagName === 'IMG' && 
            e.target.closest('.edit_invoice_button, .edit_button')) {
            const container = e.target.closest('.edit_invoice_button, .edit_button');
            handleEditClick(container);
            return;
        }
        
        // 3. Клик по тексту "Редактировать" внутри
        if (e.target.classList.contains('open-btn') && 
            e.target.textContent.includes('Редактировать')) {
            const container = e.target.closest('.edit_invoice_button, .edit_button');
            if (container) {
                handleEditClick(container);
            }
            return;
        }
    });
    
    console.log('Обработчики редактирования настроены');
}

function handleEditClick(container) {
    const invoiceId = container.getAttribute('data-id');
    
    if (!invoiceId) {
        console.error('Нет data-id у элемента:', container);
        return;
    }
    
    console.log(`Редактирование накладной ID: ${invoiceId}`);
    
    // Загружаем и заполняем форму
    loadInvoiceAndPopulateForm(invoiceId);
}

// Упрощенная функция загрузки
async function loadInvoiceAndPopulateForm(invoiceId) {
    try {
        const response = await fetch(`/comers/edit_invoices/${invoiceId}/`);
        const data = await response.json();
        
        // Заполняем форму простым способом
        fillFormSimple(data);
        
        // Показываем popup5
        document.getElementById('popup5').style.display = 'block';
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось загрузить данные');
    }
}

// Простое заполнение формы
function fillFormSimple(data) {
    const form = document.getElementById('invoice_edit_form');
    if (!form) return;
    
    // Извлекаем ID
    const getValue = (field) => {
        if (!field) return '';
        if (typeof field === 'object' && field.id) return field.id;
        return field;
    };
    
    // Заполняем основные поля
    const fields = [
        { name: 'invoice_number', value: data.invoice_number },
        { name: 'date', value: data.date?.split('T')[0] },
        { name: 'supplier', value: getValue(data.supplier) },
        { name: 'name', value: data.name },
        { name: 'quantity', value: data.quantity },
        { name: 'comment', value: getValue(data.comment) },
        { name: 'description_problem', value: data.description_problem },
        { name: 'specialist', value: getValue(data.specialist) },
        { name: 'leading', value: getValue(data.leading) },
    ];
    
    fields.forEach(field => {
        const input = form.querySelector(`[name="${field.name}"]`);
        if (input && field.value !== undefined) {
            input.value = field.value || '';
        }
    });
    
    // ID накладной
    let idField = form.querySelector('#invoice_id');
    if (!idField) {
        idField = document.createElement('input');
        idField.type = 'hidden';
        idField.name = 'invoice_id';
        form.appendChild(idField);
    }
    idField.value = data.id;
}

// Инициализация
document.addEventListener('DOMContentLoaded', setupEditHandlers);