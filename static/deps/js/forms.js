class FormHandler {
  constructor(formId, options = {}) {
    this.form = document.getElementById(formId);
    if (!this.form) return;

    this.submitButton = this.form.querySelector('.rehab-btn');
    this.buttonText = this.submitButton.querySelector('.button-text');
    this.spinner = this.submitButton.querySelector('.spinner-border');
    this.successModal = new bootstrap.Modal(
      document.getElementById('successModal')
    );
    this.errorModal = new bootstrap.Modal(
      document.getElementById('errorModal')
    );
    this.errorMessage = document.getElementById('errorMessage');
    this.requestNumber = document.getElementById('requestNumber');

    // Настройки по умолчанию
    this.options = {
      phoneInputId: 'phone',
      phoneErrorId: 'phoneError',
      ...options,
    };

    this.phoneInput = document.getElementById(this.options.phoneInputId);
    this.phoneError = document.getElementById(this.options.phoneErrorId);

    this.init();
  }

  init() {
    if (this.phoneInput) {
      this.phoneInput.addEventListener('input', this.validatePhone.bind(this));
    }

    this.form.addEventListener('submit', this.handleSubmit.bind(this));

    // Обработчик закрытия модального окна успеха
    if (this.successModal) {
      const successModalElement = document.getElementById('successModal');
      successModalElement.addEventListener('hidden.bs.modal', () => {
        this.cleanupModal();
      });
      // Добавляем обработчик для крестика
      const closeButton = successModalElement.querySelector('.btn-close');
      if (closeButton) {
        closeButton.addEventListener('click', () => {
          this.successModal.hide();
        });
      }
    }

    // Обработчик закрытия модального окна ошибки
    if (this.errorModal) {
      const errorModalElement = document.getElementById('errorModal');
      errorModalElement.addEventListener('hidden.bs.modal', () => {
        this.cleanupModal();
      });
      // Добавляем обработчик для крестика
      const closeButton = errorModalElement.querySelector('.btn-close');
      if (closeButton) {
        closeButton.addEventListener('click', () => {
          this.errorModal.hide();
        });
      }
    }
  }

  cleanupModal() {
    // Удаляем все backdrop
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach((backdrop) => backdrop.remove());

    // Удаляем класс modal-open с body
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    // Сбрасываем форму
    this.form.reset();
  }

  validatePhone(e) {
    const phone = e.target.value;
    const phoneRegex = /^\+7\s?\(?\d{3}\)?\s?\d{3}-?\d{2}-?\d{2}$/;

    if (!phoneRegex.test(phone)) {
      this.phoneError.textContent =
        'Введите номер в формате: +7 (XXX) XXX-XX-XX';
      this.phoneInput.classList.add('is-invalid');
    } else {
      this.phoneError.textContent = '';
      this.phoneInput.classList.remove('is-invalid');
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    // Показываем состояние загрузки
    this.buttonText.textContent = 'Отправка...';
    this.spinner.classList.remove('d-none');
    this.submitButton.disabled = true;

    try {
      const formData = new FormData(this.form);
      const response = await fetch(this.form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Успешная отправка
        this.requestNumber.textContent = data.request_number;
        this.successModal.show();
      } else {
        // Ошибка
        this.errorMessage.textContent =
          data.error ||
          'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';
        this.errorModal.show();
      }
    } catch (error) {
      this.errorMessage.textContent =
        'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';
      this.errorModal.show();
    } finally {
      // Возвращаем кнопку в исходное состояние
      this.buttonText.textContent = 'Оставить заявку';
      this.spinner.classList.add('d-none');
      this.submitButton.disabled = false;
    }
  }
}

// Инициализация форм при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
  // Форма консультации
  new FormHandler('consultationForm', {
    phoneInputId: 'phone',
    phoneErrorId: 'phoneError',
  });

  // Форма помощи
  new FormHandler('rehabHelpForm', {
    phoneInputId: 'rehab-phone',
    phoneErrorId: 'rehabPhoneError',
  });
});
