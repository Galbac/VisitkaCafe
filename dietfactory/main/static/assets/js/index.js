// index.js — Специфичная логика главной страницы (галерея, форма обратной связи, анимация блока "О нас")
document.addEventListener('DOMContentLoaded', function () {

    // 1. Анимация появления блока "О нас" при скролле
    const aboutSection = document.querySelector('.about-section');
    if (aboutSection) {
        function checkAboutVisibility() {
            const rect = aboutSection.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.85) {
                aboutSection.classList.add('show');
                window.removeEventListener('scroll', checkAboutVisibility);
            }
        }
        checkAboutVisibility();
        window.addEventListener('scroll', checkAboutVisibility);
    }

    // 2. Модальное окно галереи изображений
    const modal = document.getElementById("modal");
    const modalImg = document.getElementById("modal-img");
    const modalCaption = document.getElementById("modal-caption");
    const modalClose = document.querySelector(".modal-close");
    const modalPrev = document.querySelector(".modal-prev");
    const modalNext = document.querySelector(".modal-next");
    const modalOverlay = document.querySelector(".modal-overlay");

    const galleryImages = Array.from(document.querySelectorAll(".gallery-item img"));
    let currentIndex = 0;

    function showImage(index) {
        if (!galleryImages.length) return;
        if (index < 0) index = galleryImages.length - 1;
        if (index >= galleryImages.length) index = 0;
        currentIndex = index;
        if (modalImg) modalImg.src = galleryImages[index].src;
        if (modalCaption) modalCaption.textContent = galleryImages[index].alt || "";

        if (modalPrev) modalPrev.style.display = galleryImages.length > 1 ? "block" : "none";
        if (modalNext) modalNext.style.display = galleryImages.length > 1 ? "block" : "none";
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = "none";
        }, 300);
    }

    if (modal) {
        galleryImages.forEach((img, index) => {
            img.addEventListener("click", () => {
                modal.style.display = "flex";
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
                showImage(index);
            });
        });

        if (modalClose) modalClose.addEventListener("click", closeModal);
        if (modalOverlay) modalOverlay.addEventListener("click", closeModal);

        if (modalNext) {
            modalNext.addEventListener("click", (e) => {
                e.stopPropagation();
                showImage(currentIndex + 1);
            });
        }

        if (modalPrev) {
            modalPrev.addEventListener("click", (e) => {
                e.stopPropagation();
                showImage(currentIndex - 1);
            });
        }

        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        document.addEventListener("keydown", (e) => {
            if (modal.classList.contains('show')) {
                if (e.key === "ArrowLeft") {
                    showImage(currentIndex - 1);
                } else if (e.key === "ArrowRight") {
                    showImage(currentIndex + 1);
                } else if (e.key === "Escape") {
                    closeModal();
                }
            }
        });
    }

    // 3. Отправка формы контактов через AJAX
    const contactForm = document.getElementById('contactForm');
    const contactFormMsg = document.getElementById('contactFormMsg');
    const submitBtn = document.getElementById('submit-btn');

    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Отправка...';
            }

            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

            fetch('/contact/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(resData => {
                if (contactFormMsg) {
                    contactFormMsg.textContent = resData.message;
                    contactFormMsg.className = resData.success ? 'form-message success show' : 'form-message error show';
                }

                if (resData.success) {
                    contactForm.reset();
                }
            })
            .catch(err => {
                console.error('Ошибка отправки формы:', err);
                if (contactFormMsg) {
                    contactFormMsg.textContent = 'Ошибка соединения. Пожалуйста, попробуйте позже или напишите нам в WhatsApp.';
                    contactFormMsg.className = 'form-message error show';
                }
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Отправить сообщение';
                }
            });
        });
    }
});
