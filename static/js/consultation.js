document.addEventListener('DOMContentLoaded', function () {
    const consultationForm = document.getElementById('consultationForm');
    if (!consultationForm) return;

    consultationForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const phoneInput = document.getElementById('phone');
        const phoneError = document.getElementById('phoneError');
        const phonePattern = /^\+7\s?\(?\d{3}\)?\s?\d{3}-?\d{2}-?\d{2}$/;

        if (!phonePattern.test(phoneInput.value)) {
            phoneError.textContent = 'Введите корректный номер телефона в формате: +7 (XXX) XXX-XX-XX';
            phoneInput.classList.add('is-invalid');
            return false;
        }

        phoneInput.classList.remove('is-invalid');
        phoneError.textContent = '';

        // Отправка формы через AJAX
        const formData = new FormData(this);
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Показываем модальное окно успеха
                    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                    document.getElementById('requestNumber').textContent = data.request_number || '12345';
                    successModal.show();
                    this.reset();
                } else {
                    // Показываем модальное окно ошибки
                    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                    document.getElementById('errorMessage').textContent = data.error || 'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';
                    errorModal.show();
                }
            })
            .catch(error => {
                // Показываем модальное окно ошибки при проблемах с сетью
                const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                document.getElementById('errorMessage').textContent = 'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';
                errorModal.show();
            });

        return false;
    });

    // Маска для телефона
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function (e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
            e.target.value = !x[2] ? x[1] : '+7 (' + x[2] + ') ' + (x[3] ? x[3] + '-' + x[4] : x[3]) + (x[5] ? '-' + x[5] : '');
        });
    }
}); 