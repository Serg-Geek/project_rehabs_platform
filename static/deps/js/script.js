document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".navbar");
    const navbarMobile = document.querySelector(".navbar__mobile");
    const menu = document.querySelector(".menu");
    const burgerMenu = document.querySelector("#burgerMenu");
    const dropdownMenu = document.querySelector("#dropdownMenu");
    const filterForm = document.getElementById("filter-form");
    const categorySelect = document.getElementById("category");

    let lastScrollTop = 0;
    let isScrolling = false;

    // Функция debounce для оптимизации обработчика скролла
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Функция переключения мобильной версии
    function toggleMobileVersion() {
        const isMobile = window.innerWidth <= 841;
        if (navbar) {
            navbar.style.display = isMobile ? 'none' : 'flex';
        }
        if (navbarMobile) {
            navbarMobile.style.display = isMobile ? 'block' : 'none';
        }
        if (menu) {
            menu.style.display = isMobile ? 'none' : 'flex';
        }
    }

    // Обработчик скролла
    const handleScroll = debounce(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        // Управление фиксированным состоянием .navbar__mobile
        if (navbarMobile) {
            if (scrollTop > 50) {
                navbarMobile.classList.add("fixed");
            } else {
                navbarMobile.classList.remove("fixed");
            }
        }

        // Управление скрытием/показом основного навбара
        if (navbar) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                navbar.style.transform = "translateY(-100%)";
                navbar.style.opacity = "0";
            } else {
                navbar.style.transform = "translateY(0)";
                navbar.style.opacity = "1";
            }
        }

        // Фиксация меню при скроле вниз
        if (menu) {
            if (scrollTop > 50) {
                menu.classList.add("fixed");
            } else {
                menu.classList.remove("fixed");
            }
        }

        lastScrollTop = Math.max(0, scrollTop);
    }, 100);

    // Функция закрытия меню
    function closeMenu() {
        if (burgerMenu && dropdownMenu) {
            burgerMenu.classList.remove("active");
            dropdownMenu.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    // Открытие/закрытие бургер-меню
    if (burgerMenu && dropdownMenu) {
        burgerMenu.addEventListener("click", (event) => {
            burgerMenu.classList.toggle("active");
            dropdownMenu.classList.toggle("active");
            document.body.style.overflow = dropdownMenu.classList.contains("active") ? "hidden" : "";
            event.stopPropagation();
        });
    }

    // Закрытие при клике на пустое место
    document.addEventListener("click", (event) => {
        if (dropdownMenu && burgerMenu) {
            if (!dropdownMenu.contains(event.target) && !burgerMenu.contains(event.target)) {
                closeMenu();
            }
        }
    });

    // Закрытие при нажатии Escape
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    // Инициализация при загрузке
    toggleMobileVersion();
    window.addEventListener("resize", toggleMobileVersion);
    window.addEventListener("scroll", handleScroll);
    initCustomSelect();

    // Отслеживаем изменение значения в <select>
    if (categorySelect) {
        categorySelect.addEventListener("change", function () {
            // Автоматически отправляем форму
            filterForm.submit();
        });
    }

    // Функция для инициализации слайдера
    function initSlider(selector, prevButton, nextButton, settings) {
        if (document.querySelector(selector)) {
            const slider = $(selector).slick(settings);

            if (
                document.querySelector(prevButton) &&
                document.querySelector(nextButton)
            ) {
                $(prevButton).on("click", function () {
                    slider.slick("slickPrev");
                });

                $(nextButton).on("click", function () {
                    slider.slick("slickNext");
                });
            }
        }
    }

    // Инициализация слайдера документов
    initSlider(
        ".detail-docs__slider",
        ".custom-prev-docs",
        ".custom-next-docs",
        {
            slidesToShow: 3,
            slidesToScroll: 1,
            arrows: false,
            dots: true,
            autoplay: true,
            autoplaySpeed: 2000,
            responsive: [
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 2,
                    },
                },
                {
                    breakpoint: 480,
                    settings: {
                        slidesToShow: 1,
                    },
                },
            ],
        }
    );

    // Инициализация слайдера отзывов
    initSlider(
        ".detail__reviews-slider",
        ".custom-prev-reviews",
        ".custom-next-reviews",
        {
            slidesToShow: 3,
            slidesToScroll: 1,
            arrows: false,
            dots: true,
            autoplay: true,
            autoplaySpeed: 3000,
            responsive: [
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 2,
                    },
                },
                {
                    breakpoint: 480,
                    settings: {
                        slidesToShow: 1,
                    },
                },
            ],
        }
    );

    // Функция инициализации кастомного селекта
    function initCustomSelect() {
        console.log('Инициализация кастомного селекта');
        const customSelect = document.querySelector('.custom-select');
        if (!customSelect) {
            console.log('Кастомный селект не найден');
            return;
        }
        console.log('Кастомный селект найден');

        const selected = customSelect.querySelector('.custom-select__selected');
        const options = customSelect.querySelector('.custom-select__options');
        const select = document.querySelector('#category');

        if (!selected || !options || !select) {
            console.log('Не найдены необходимые элементы селекта');
            return;
        }
        console.log('Все элементы селекта найдены');

        // Открытие/закрытие выпадающего списка
        selected.addEventListener('click', function (e) {
            console.log('Клик по выбранному элементу');
            e.stopPropagation();
            customSelect.classList.toggle('active');
            options.classList.toggle('active');
        });

        // Выбор опции
        options.querySelectorAll('.custom-select__option').forEach(option => {
            option.addEventListener('click', function (e) {
                console.log('Клик по опции');
                e.stopPropagation();
                const value = this.dataset.value;
                const text = this.textContent;

                // Обновляем текст выбранной опции
                selected.textContent = text;

                // Обновляем значение скрытого select
                select.value = value;

                // Закрываем выпадающий список
                customSelect.classList.remove('active');
                options.classList.remove('active');

                // Отправляем форму
                filterForm.submit();
            });
        });

        // Закрытие при клике вне селекта
        document.addEventListener('click', function (e) {
            if (!customSelect.contains(e.target)) {
                customSelect.classList.remove('active');
                options.classList.remove('active');
            }
        });

        // Установка начального значения
        if (select.value) {
            const option = options.querySelector(`[data-value="${select.value}"]`);
            if (option) {
                selected.textContent = option.textContent;
            }
        }
    }

    // Обработка формы консультации
    const consultationForm = document.getElementById('consultationForm');
    if (consultationForm) {
        console.log('Форма консультации найдена');

        consultationForm.addEventListener('submit', function (e) {
            e.preventDefault();
            console.log('Отправка формы консультации');

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
                .then(response => {
                    console.log('Получен ответ от сервера');
                    return response.json();
                })
                .then(data => {
                    console.log('Данные ответа:', data);

                    if (data.success) {
                        // Показываем модальное окно успеха
                        console.log('Показываем модальное окно успеха');
                        const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                        document.getElementById('requestNumber').textContent = data.request_number || '12345';

                        // Добавляем обработчик события закрытия модального окна
                        document.getElementById('successModal').addEventListener('hidden.bs.modal', function () {
                            // Удаляем backdrop при закрытии модального окна
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) {
                                backdrop.remove();
                            }
                            // Удаляем класс modal-open с body
                            document.body.classList.remove('modal-open');
                            // Удаляем стиль overflow с body
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        });

                        successModal.show();
                        this.reset();
                    } else {
                        // Показываем модальное окно ошибки
                        console.log('Показываем модальное окно ошибки');
                        const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                        document.getElementById('errorMessage').textContent = data.error || 'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';

                        // Добавляем обработчик события закрытия модального окна
                        document.getElementById('errorModal').addEventListener('hidden.bs.modal', function () {
                            // Удаляем backdrop при закрытии модального окна
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) {
                                backdrop.remove();
                            }
                            // Удаляем класс modal-open с body
                            document.body.classList.remove('modal-open');
                            // Удаляем стиль overflow с body
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        });

                        errorModal.show();
                    }
                })
                .catch(error => {
                    console.error('Ошибка при отправке формы:', error);
                    // Показываем модальное окно ошибки при проблемах с сетью
                    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                    document.getElementById('errorMessage').textContent = 'Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.';

                    // Добавляем обработчик события закрытия модального окна
                    document.getElementById('errorModal').addEventListener('hidden.bs.modal', function () {
                        // Удаляем backdrop при закрытии модального окна
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) {
                            backdrop.remove();
                        }
                        // Удаляем класс modal-open с body
                        document.body.classList.remove('modal-open');
                        // Удаляем стиль overflow с body
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    });

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
    } else {
        console.log('Форма консультации не найдена');
    }
});

