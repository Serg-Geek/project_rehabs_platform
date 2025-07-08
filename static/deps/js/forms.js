// Функция маски ввода для телефонных номеров
function initPhoneMask(phoneInput) {
  if (!phoneInput) return;

  // Используем библиотеку inputmask для создания маски
  $(phoneInput).inputmask({
    mask: '+7 (999) 999-99-99',
    placeholder: '+7 (XXX) XXX-XX-XX',
    showMaskOnHover: true,
    showMaskOnFocus: true,
    onBeforePaste: function (pastedValue, opts) {
      // Очищаем вставляемое значение от всех символов кроме цифр
      const processedValue = pastedValue.replace(/\D/g, '');
      return processedValue;
    },
    onBeforeMask: function (value, opts) {
      // Обрабатываем значение перед применением маски
      if (value && !value.startsWith('+7')) {
        // Если номер не начинается с +7, добавляем его
        return '+7' + value.replace(/\D/g, '');
      }
      return value;
    }
  });
}

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
      // Применяем маску ввода
      initPhoneMask(this.phoneInput);
      // Добавляем валидацию
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
    // Проверяем, что номер полностью заполнен (все 10 цифр после +7)
    const digitsOnly = phone.replace(/\D/g, '');
    const hasEnoughDigits = digitsOnly.length >= 11; // +7 + 10 цифр
    
    // Проверяем формат с помощью inputmask
    const isComplete = phone.replace(/[_\s]/g, '').length === 18; // +7 (999) 999-99-99 = 18 символов

    if (!hasEnoughDigits || !isComplete) {
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

  // Форма контактной информации
  new FormHandler('contactInfoForm', {
    phoneInputId: 'contact-phone',
    phoneErrorId: 'contactPhoneError',
  });

  // Форма партнеров
  new FormHandler('partnerForm', {
    phoneInputId: 'partner-phone',
    phoneErrorId: 'partnerPhoneError',
  });

  // Форма на странице контактов
  const contactInput = document.getElementById('contact-input');
  if (contactInput) {
    initPhoneMask(contactInput);
  }
});
