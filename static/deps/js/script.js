document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".navbar");
    const navbarMobile = document.querySelector(".navbar__mobile");
    const menu = document.querySelector(".menu");
    const burgerMenu = document.querySelector("#burgerMenu");
    const dropdownMenu = document.querySelector("#dropdownMenu");
    const filterForm = document.getElementById("filter-form");
    const categorySelect = document.getElementById("category");

    let lastScrollTop = 0;

    // Скрытие навбара при скролле вниз
    window.addEventListener("scroll", () => {
        const scrollTop =
            window.pageYOffset || document.documentElement.scrollTop;

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
            navbar.style.transform =
                scrollTop > lastScrollTop
                    ? "translateY(-100%)"
                    : "translateY(0)";
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
    });

    // Функция закрытия меню
    function closeMenu() {
        burgerMenu.classList.remove("active");
        dropdownMenu.classList.remove("active");
    }

    // Открытие/закрытие бургер-меню
    burgerMenu.addEventListener("click", (event) => {
        burgerMenu.classList.toggle("active");
        dropdownMenu.classList.toggle("active");
        event.stopPropagation(); // Остановить всплытие, чтобы не закрывать меню сразу
    });

    // Закрытие при клике на пустое место
    document.addEventListener("click", (event) => {
        if (
            !dropdownMenu.contains(event.target) &&
            !burgerMenu.contains(event.target)
        ) {
            closeMenu();
        }
    });

    // Закрытие при нажатии Escape
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

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
});
