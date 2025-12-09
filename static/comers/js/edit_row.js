// document.addEventListener('DOMContentLoaded', function() {
//     console.log('=== СИСТЕМА РЕДАКТИРОВАНИЯ ===');
//     console.log('Ищем кнопки с классом open-btn и текстом "Редактировать"');
    
//     // Вешаем обработчик на open-btn
//     document.addEventListener('click', async function(e) {
//         // Находим элемент с классом open-btn
//         const openBtn = e.target.closest('.open-btn');
        
//         if (openBtn && openBtn.textContent.trim() === 'Редактировать') {
//             e.preventDefault();
//             e.stopPropagation();
            
//             console.log('✅ Клик по кнопке "Редактировать"');
//             console.log('Элемент:', openBtn);
            
//             // Теперь ищем data-id
            
//             // Вариант 1: Ищем в том же контейнере что и open-btn
//             const container = openBtn.closest('tr, .row, .item, [data-id]') || 
//                             openBtn.parentElement;
            
//             console.log('Контейнер:', container);
//             console.log('Классы контейнера:', container.className);
            
//             // Вариант 2: Ищем delete_button рядом
//             let dataId = null;
//             let foundElement = null;
            
//             // Способ A: Ищем любой элемент с data-id в контейнере
//             const elementsWithDataId = container.querySelectorAll('[data-id]');
//             console.log(`Найдено элементов с data-id: ${elementsWithDataId.length}`);
            
//             elementsWithDataId.forEach((el, i) => {
//                 console.log(`${i}. ${el.className} - data-id: ${el.getAttribute('data-id')}`);
                
//                 // Предпочитаем delete_button если есть
//                 if (el.classList.contains('delete_button') && !dataId) {
//                     dataId = el.getAttribute('data-id');
//                     foundElement = el;
//                     console.log('Выбрали delete_button');
//                 }
//             });
            
//             // Если не нашли delete_button, берем первый data-id
//             if (!dataId && elementsWithDataId.length > 0) {
//                 dataId = elementsWithDataId[0].getAttribute('data-id');
//                 foundElement = elementsWithDataId[0];
//                 console.log('Взяли первый data-id элемент');
//             }
            
//             // Способ B: Ищем в родителях open-btn
//             if (!dataId) {
//                 let parent = openBtn.parentElement;
//                 for (let i = 0; i < 5; i++) {
//                     if (parent && parent.hasAttribute('data-id')) {
//                         dataId = parent.getAttribute('data-id');
//                         foundElement = parent;
//                         console.log(`Нашли в родителе уровня ${i}`);
//                         break;
//                     }
//                     parent = parent.parentElement;
//                 }
//             }
            
//             if (dataId) {
//                 console.log(`✅ Найден data-id: ${dataId}`);
//                 console.log(`Элемент с data-id:`, foundElement);
                
//                 // Загружаем и заполняем форму
//                 await loadAndPopulateForm(dataId);
                
//             } else {
//                 console.error('❌ data-id не найден!');
//                 console.log('Структура для отладки:');
//                 console.log('open-btn родитель:', openBtn.parentElement.outerHTML);
//                 console.log('open-btn дедушка:', openBtn.parentElement.parentElement?.outerHTML);
                
//                 // Показываем все data-id на странице для отладки
//                 const allDataIds = document.querySelectorAll('[data-id]');
//                 console.log(`Всего элементов с data-id на странице: ${allDataIds.length}`);
//                 allDataIds.forEach((el, i) => {
//                     console.log(`${i}. ${el.className}: ${el.getAttribute('data-id')}`);
//                 });
//             }
//         }
//     });
    
//     console.log('Обработчик установлен. Кликните "Редактировать"');
// });

// // Функция загрузки и заполнения формы
// async function loadAndPopulateForm(invoiceId) {
//     console.log(`=== ЗАГРУЗКА ДАННЫХ ДЛЯ ID: ${invoiceId} ===`);
    
//     // Показываем индикатор загрузки
//     showLoading(true);
    
//     try {
//         // Загружаем данные
//         const response = await fetch(`/comers/edit_invoices/${invoiceId}/`, {
//             method: 'GET',
//             headers: {
//                 'Accept': 'application/json'
//             }
//         });
        
//         console.log('Статус ответа:', response.status);
        
//         if (response.ok) {
//             const invoiceData = await response.json();
//             console.log('✅ Данные получены:', invoiceData);
            
//             // Заполняем форму
//             populateForm(invoiceData);
            
//             // Показываем модальное окно (popup5 согласно data-popup)
//             showModal('popup5');
            
//         } else {
//             console.error('Ошибка сервера:', response.status);
//             const errorText = await response.text();
//             console.error('Текст ошибки:', errorText);
//             alert('Не удалось загрузить данные');
//         }
        
//     } catch (error) {
//         console.error('Ошибка сети:', error);
//         alert('Ошибка сети при загрузке данных');
//     } finally {
//         showLoading(false);
//     }
// }

// // Функция заполнения формы
// function populateForm(data) {
//     console.log('=== ЗАПОЛНЕНИЕ ФОРМЫ ===');
    
//     const form = document.getElementById('invoice_edit_form');
//     if (!form) {
//         console.error('Форма invoice_edit_form не найдена!');
        
//         // Ищем другие возможные формы
//         const possibleForms = ['invoice_edit_form', 'editForm', 'formEdit'];
//         possibleForms.forEach(formId => {
//             const f = document.getElementById(formId);
//             if (f) console.log(`Найдена форма: ${formId}`);
//         });
        
//         return;
//     }
    
//     console.log('Форма найдена, заполняем...');
    
//     // Маппинг полей: имя_поля_в_форме -> ключ_в_данных
//     const fieldMap = {
//         'invoice_number': data.invoice_number || '',
//         'date': formatDate(data.date) || '',
//         'supplier': data.supplier || data.supplier_id || '',
//         'article_mirror': data.article || '',
//         'name': data.name || '',
//         'quantity': data.quantity || '',
//         'comment': data.comment || data.comment_id || '',
//         'description_problem': data.description_problem || '',
//         'specialist': data.specialist || data.specialist_id || '',
//         'leading': data.leading || data.leading_id || '',
//     };
    
//     // Заполняем каждое поле
//     Object.entries(fieldMap).forEach(([fieldName, value]) => {
//         const input = form.querySelector(`[name="${fieldName}"]`);
//         if (input) {
//             input.value = value;
//             console.log(`✓ ${fieldName}: ${value}`);
//         } else {
//             console.warn(`✗ Поле ${fieldName} не найдено`);
//         }
//     });
    
//     // Скрытые поля
//     const hiddenFields = {
//         'unit': data.unit || '',
//         'article': data.article || '',
//         'project': data.project || ''
//     };
    
//     Object.entries(hiddenFields).forEach(([fieldName, value]) => {
//         const input = form.querySelector(`[name="${fieldName}"]`);
//         if (input) {
//             input.value = value;
//             console.log(`✓ Скрытое ${fieldName}: ${value}`);
//         }
//     });
    
//     // Добавляем ID в скрытое поле
//     let idField = form.querySelector('#invoice_id_field');
//     if (!idField) {
//         idField = document.createElement('input');
//         idField.type = 'hidden';
//         idField.id = 'invoice_id_field';
//         idField.name = 'invoice_id';
//         form.appendChild(idField);
//     }
//     idField.value = data.id;
//     console.log(`✓ ID накладной: ${data.id}`);
// }

// // Форматирование даты
// function formatDate(dateString) {
//     if (!dateString) return '';
    
//     try {
//         // Если дата в формате ISO
//         if (dateString.includes('T')) {
//             return dateString.split('T')[0];
//         }
//         return dateString;
//     } catch (e) {
//         return dateString;
//     }
// }

// // Показать/скрыть индикатор загрузки
// function showLoading(show) {
//     const loader = document.getElementById('loadingIndicator');
//     if (!loader && show) {
//         // Создаем индикатор если его нет
//         const newLoader = document.createElement('div');
//         newLoader.id = 'loadingIndicator';
//         newLoader.innerHTML = `
//             <div style="
//                 position: fixed;
//                 top: 50%;
//                 left: 50%;
//                 transform: translate(-50%, -50%);
//                 background: white;
//                 padding: 20px;
//                 border-radius: 10px;
//                 box-shadow: 0 0 10px rgba(0,0,0,0.3);
//                 z-index: 9999;
//             ">
//                 <div style="
//                     border: 4px solid #f3f3f3;
//                     border-top: 4px solid #3498db;
//                     border-radius: 50%;
//                     width: 40px;
//                     height: 40px;
//                     animation: spin 1s linear infinite;
//                     margin: 0 auto 15px;
//                 "></div>
//                 <p>Загрузка данных...</p>
//             </div>
//         `;
//         document.body.appendChild(newLoader);
//     }
    
//     if (loader) {
//         loader.style.display = show ? 'block' : 'none';
//     }
// }

// // Показать модальное окно
// function showModal(modalId) {
//     const modal = document.getElementById(modalId);
//     if (modal) {
//         modal.style.display = 'block';
//         console.log(`Модальное окно ${modalId} показано`);
//     } else {
//         console.error(`Модальное окно ${modalId} не найдено!`);
        
//         // Ищем другие модальные окна
//         const modals = document.querySelectorAll('.modal, .popup');
//         console.log(`Найдено модальных окон: ${modals.length}`);
//         modals.forEach(m => console.log(m.id));
//     }
// }