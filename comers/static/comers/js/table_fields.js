// document.getElementById('input_data_form').addEventListener('submit', function(event) {
//     event.preventDefault();
//     const formData = new FormData(this);

//     fetch("{% url '/comers/add_supplier/' %}", {
//         method: 'POST',
//         body: formData,
//         headers: {
//             'X-CSRFToken': '{{ csrf_token }}',
//         }
//     })})