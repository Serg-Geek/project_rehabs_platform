document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".navbar");
    const navbarMobile = document.querySelector(".navbar__mobile");
    const menu = document.querySelector(".menu");
    const burgerMenu = document.querySelector("#burgerMenu");
    const dropdownMenu = document.querySelector("#dropdownMenu");
    const loadMoreRehabsButton = document.getElementById("loadMoreRehabs");
    const loadMoreClinicsButton = document.getElementById("loadMoreClinics");

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
        const customSelects = document.querySelectorAll('.custom-select');
        if (!customSelects.length) {
            console.log('Кастомные селекты не найдены');
            return;
        }
        console.log(`Найдено ${customSelects.length} кастомных селектов`);

        customSelects.forEach((customSelect, index) => {
            const selected = customSelect.querySelector('.custom-select__selected');
            const options = customSelect.querySelector('.custom-select__options');
            const select = customSelect.querySelector('select');

            if (!selected || !options || !select) {
                console.log(`Не найдены необходимые элементы селекта ${index + 1}`);
                return;
            }
            console.log(`Инициализация селекта ${index + 1}`);

            // Открытие/закрытие выпадающего списка
            selected.addEventListener('click', function (e) {
                console.log(`Клик по выбранному элементу селекта ${index + 1}`);
                e.stopPropagation();
                
                // Закрываем все другие селекты
                customSelects.forEach((otherSelect, otherIndex) => {
                    if (otherIndex !== index) {
                        otherSelect.classList.remove('active');
                        otherSelect.querySelector('.custom-select__options').classList.remove('active');
                    }
                });
                
                customSelect.classList.toggle('active');
                options.classList.toggle('active');
            });

            // Выбор опции
            options.querySelectorAll('.custom-select__option').forEach(option => {
                option.addEventListener('click', function (e) {
                    console.log(`Клик по опции селекта ${index + 1}`);
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
                    const form = customSelect.closest('form');
                    if (form) {
                        form.submit();
                    }
                });
            });

            // Установка начального значения
            if (select.value) {
                const option = options.querySelector(`[data-value="${select.value}"]`);
                if (option) {
                    selected.textContent = option.textContent;
                }
            }
        });

        // Закрытие при клике вне селектов
        document.addEventListener('click', function (e) {
            let clickedInside = false;
            customSelects.forEach(customSelect => {
                if (customSelect.contains(e.target)) {
                    clickedInside = true;
                }
            });
            
            if (!clickedInside) {
                customSelects.forEach(customSelect => {
                    customSelect.classList.remove('active');
                    const options = customSelect.querySelector('.custom-select__options');
                    if (options) {
                        options.classList.remove('active');
                    }
                });
            }
        });
    }

    // Функция для загрузки дополнительных карточек
    function initLoadMore(button, url) {
        if (button) {
            button.addEventListener('click', function() {
                button.disabled = true;
                const currentCards = document.querySelectorAll('.rehabs__cards .card').length;
                
                fetch(url + '?offset=' + currentCards, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.cards) {
                        const cardsContainer = document.querySelector('.rehabs__cards');
                        cardsContainer.insertAdjacentHTML('beforeend', data.cards);
                        if (!data.has_more) {
                            button.style.display = 'none';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    button.disabled = false;
                });
            });
        }
    }

    // Инициализация кнопок "Показать еще"
    initLoadMore(loadMoreRehabsButton, '/facilities/load-more-rehabs/');
    initLoadMore(loadMoreClinicsButton, '/facilities/load-more-clinics/');
});

