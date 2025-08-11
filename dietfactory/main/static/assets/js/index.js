document.addEventListener('DOMContentLoaded', function () {

    // --- Общая логика сайта ---

    // Search functionality
    const searchToggle = document.querySelector('.js__th_form__show');
    const searchForm = document.querySelector('.th_form');
    const searchClose = document.querySelector('.js__th_form__close');
    const searchInput = document.getElementById('js__th_search');

    if (searchToggle && searchForm) {
        searchToggle.addEventListener('click', function (e) {
            e.preventDefault();
            searchForm.classList.add('show');
            searchInput.focus();
        });

        if (searchClose) {
            searchClose.addEventListener('click', function () {
                searchForm.classList.remove('show');
            });
        }

        // Close search form when clicking outside
        document.addEventListener('click', function (e) {
            if (!searchForm.contains(e.target) && !searchToggle.contains(e.target)) {
                searchForm.classList.remove('show');
            }
        });

        // Close search form on escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                searchForm.classList.remove('show');
            }
        });
    }

    // Scroll to top button
    const btnTop = document.getElementById('btnTop');

    if (btnTop) {
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                btnTop.style.display = 'flex';
            } else {
                btnTop.style.display = 'none';
            }
        });

        btnTop.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    document.addEventListener('DOMContentLoaded', function () {
        const aboutSection = document.querySelector('.about-section');

        function checkVisibility() {
            const rect = aboutSection.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.8) {
                aboutSection.classList.add('show');
            }
        }

        // Проверяем при загрузке
        checkVisibility();
        // И при скролле
        window.addEventListener('scroll', checkVisibility);
    });

    // Mobile menu toggle (if needed)
    const mobileMenuToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.mhead__nav');

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
            document.body.classList.toggle('mobile-nav-active');
        });
    }

    // Submenu functionality
    const submenuItems = document.querySelectorAll('.flhead_item');

    submenuItems.forEach(function (item) {
        const submenu = item.querySelector('.flhead_submenu');

        if (submenu) {
            // Show submenu on hover (desktop)
            item.addEventListener('mouseenter', function () {
                if (window.innerWidth > 768) {
                    submenu.style.display = 'block';
                }
            });

            item.addEventListener('mouseleave', function () {
                if (window.innerWidth > 768) {
                    submenu.style.display = 'none';
                }
            });

            // Toggle submenu on click (mobile)
            const content = item.querySelector('.flhead_item__content');
            if (content) {
                content.addEventListener('click', function (e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
                    }
                });
            }
        }
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            if (href !== '#') {
                const target = document.querySelector(href);

                if (target) {
                    e.preventDefault();
                    const headerHeight = document.querySelector('.header').offsetHeight;
                    const targetPosition = target.offsetTop - headerHeight;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Header scroll effect
    const header = document.querySelector('.header');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function () {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            header.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            header.style.transform = 'translateY(0)';
        }

        lastScrollTop = scrollTop;
    });

    // Add loading animation for search
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            const submitBtn = this.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.value = 'Поиск...';
                submitBtn.disabled = true;

                // Reset after 2 seconds (simulate search)
                setTimeout(function () {
                    submitBtn.value = 'Find';
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    }

    // Add active state to navigation items
    const navLinks = document.querySelectorAll('.mhead__mn a');
    const currentPath = window.location.pathname;

    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Initialize tooltips (if Bootstrap is available)
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Add parallax effect to background (if exists)
    const parallaxElement = document.getElementById('fixmixed');
    if (parallaxElement) {
        window.addEventListener('scroll', function () {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            parallaxElement.style.transform = 'translateY(' + rate + 'px)';
        });
    }

    // Form validation for contact form
    const contactForm = document.querySelector('form[action="#"]');
    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const name = this.querySelector('input[name="name"]');
            const email = this.querySelector('input[name="email"]');
            const message = this.querySelector('textarea[name="message"]');

            if (!name.value || !email.value || !message.value) {
                alert('Пожалуйста, заполните все поля');
                return;
            }

            if (!isValidEmail(email.value)) {
                alert('Пожалуйста, введите корректный email');
                return;
            }

            // Simulate form submission
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            submitBtn.textContent = 'Отправляется...';
            submitBtn.disabled = true;

            setTimeout(function () {
                alert('Сообщение отправлено!');
                contactForm.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }

    // Email validation helper
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Add intersection observer for animations
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements that should animate
        const animateElements = document.querySelectorAll('.product-card, .flhead_item, .mhead__mn li');
        animateElements.forEach(function (el) {
            observer.observe(el);
        });
    }

    // Performance optimization: Debounce scroll events
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

    // Apply debouncing to scroll events
    const debouncedScrollHandler = debounce(function () {
        // Scroll event logic here
    }, 10);

    window.addEventListener('scroll', debouncedScrollHandler);

    // --- Логика модального окна галереи ---

    // Получаем элементы модального окна
    const modal = document.getElementById("modal");
    const modalImg = document.getElementById("modal-img");
    const modalCaption = document.getElementById("modal-caption");
    const modalClose = document.querySelector(".modal-close");
    const modalPrev = document.querySelector(".modal-prev");
    const modalNext = document.querySelector(".modal-next");
    const modalOverlay = document.querySelector(".modal-overlay");

    // Получаем все картинки галереи в массив
    const galleryImages = Array.from(document.querySelectorAll(".gallery-item img"));
    let currentIndex = 0;

    // Функция показа картинки по индексу
    function showImage(index) {
        if (index < 0) index = galleryImages.length - 1;
        if (index >= galleryImages.length) index = 0;
        currentIndex = index;
        modalImg.src = galleryImages[index].src;
        modalCaption.textContent = galleryImages[index].alt || "";

        // Показываем или скрываем стрелки в зависимости от количества изображений
        if (galleryImages.length > 1) {
            modalPrev.style.display = "block";
            modalNext.style.display = "block";
        } else {
            modalPrev.style.display = "none";
            modalNext.style.display = "none";
        }
    }

    // При клике на маленькую картинку открываем модал с ней
    galleryImages.forEach((img, index) => {
        img.addEventListener("click", () => {
            modal.style.display = "flex";
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
            showImage(index);
        });
    });

    // Закрыть модал
    function closeModal() {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = "none";
        }, 300);
    }

    if (modalClose) modalClose.addEventListener("click", closeModal);
    if (modalOverlay) modalOverlay.addEventListener("click", closeModal);

    // Навигация вперед
    if (modalNext) {
        modalNext.addEventListener("click", (e) => {
            e.stopPropagation();
            showImage(currentIndex + 1);
        });
    }

    // Навигация назад
    if (modalPrev) {
        modalPrev.addEventListener("click", (e) => {
            e.stopPropagation();
            showImage(currentIndex - 1);
        });
    }

    // Закрытие по клику вне картинки
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // Опционально: стрелки на клавиатуре
    document.addEventListener("keydown", (e) => {
        if (modal && modal.classList.contains('show')) {
            if (e.key === "ArrowLeft") {
                showImage(currentIndex - 1);
            } else if (e.key === "ArrowRight") {
                showImage(currentIndex + 1);
            } else if (e.key === "Escape") {
                closeModal();
            }
        }
    });

    console.log('FitAudit JavaScript loaded successfully');
});

// Export functions for use in other scripts (if needed)
window.FitAudit = {
    showSearch: function () {
        const searchForm = document.querySelector('.th_form');
        if (searchForm) {
            searchForm.classList.add('show');
            document.getElementById('js__th_search').focus();
        }
    },

    hideSearch: function () {
        const searchForm = document.querySelector('.th_form');
        if (searchForm) {
            searchForm.classList.remove('show');
        }
    },

    scrollToTop: function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
};

document.getElementById('contactForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    data['csrfmiddlewaretoken'] = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/contact/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            const msgBox = document.getElementById('contactFormMsg');
            msgBox.textContent = data.message;
            msgBox.className = data.success ? 'form-message success show' : 'form-message error show';

            if (data.success) {
                this.reset();
            }
        })
        .catch(err => {
            console.error('Ошибка:', err);
            document.getElementById('contactFormMsg').textContent = 'Ошибка соединения.';
            document.getElementById('contactFormMsg').className = 'form-message error show';
        });
});