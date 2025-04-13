class FormHandler {
  constructor(formId, submitButtonId, phoneInputId, phoneErrorId) {
    this.form = document.getElementById(formId);
    this.submitButton = document.getElementById(submitButtonId);
    this.phoneInput = document.getElementById(phoneInputId);
    this.phoneError = document.getElementById(phoneErrorId);
    this.buttonText = this.submitButton.querySelector('.button-text');
    this.spinner = this.submitButton.querySelector('.spinner-border');
    this.init();
  }

  init() {
    if (this.form) {
      this.form.addEventListener('submit', this.handleSubmit.bind(this));
      if (this.phoneInput) {
        this.phoneInput.addEventListener('input', this.formatPhoneNumber.bind(this));
      }
    }
  }

  formatPhoneNumber(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 0) {
      value = value.match(new RegExp('.{1,' + (value.length > 11 ? 11 : value.length) + '}', 'g')).join('');
      let formattedValue = '+7';
      
      if (value.length > 1) {
        formattedValue += ' (' + value.substring(1, 4);
      }
      if (value.length > 4) {
        formattedValue += ') ' + value.substring(4, 7);
      }
      if (value.length > 7) {
        formattedValue += '-' + value.substring(7, 9);
      }
      if (value.length > 9) {
        formattedValue += '-' + value.substring(9, 11);
      }
      
      input.value = formattedValue;
    }
  }

  async handleSubmit(event) {
    event.preventDefault();
    
    if (this.phoneInput && !this.validatePhoneNumber(this.phoneInput.value)) {
      this.phoneError.textContent = 'Пожалуйста, введите корректный номер телефона';
      this.phoneInput.classList.add('is-invalid');
      return;
    }

    this.showLoading();

    try {
      const formData = new FormData(this.form);
      formData.append('source', 'partner'); // Добавляем метку для партнеров

      const response = await fetch(this.form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const data = await response.json();

      if (data.success) {
        this.showSuccessModal();
        this.form.reset();
      } else {
        this.showErrorModal(data.message || 'Произошла ошибка при отправке формы');
      }
    } catch (error) {
      this.showErrorModal('Произошла ошибка при отправке формы');
    } finally {
      this.hideLoading();
    }
  }

  validatePhoneNumber(phone) {
    const phoneRegex = /^\+7\s?\(?\d{3}\)?\s?\d{3}-?\d{2}-?\d{2}$/;
    return phoneRegex.test(phone);
  }

  showLoading() {
    this.buttonText.classList.add('d-none');
    this.spinner.classList.remove('d-none');
    this.submitButton.disabled = true;
  }

  hideLoading() {
    this.buttonText.classList.remove('d-none');
    this.spinner.classList.add('d-none');
    this.submitButton.disabled = false;
  }

  showSuccessModal() {
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    successModal.show();
  }

  showErrorModal(message) {
    const errorModal = document.getElementById('errorModal');
    const errorMessage = errorModal.querySelector('.modal-body');
    errorMessage.textContent = message;
    const modal = new bootstrap.Modal(errorModal);
    modal.show();
  }
}

// Инициализация форм
document.addEventListener('DOMContentLoaded', () => {
  new FormHandler('consultationForm', 'consultationSubmitButton', 'phone', 'phoneError');
  new FormHandler('partnerForm', 'partnerSubmitButton', 'partner-phone', 'partnerPhoneError');
}); 