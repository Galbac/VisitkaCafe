document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contactForm');
    const msg = document.getElementById('contactFormMsg');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Скрываем предыдущее сообщение и удаляем классы
            msg.classList.remove('show', 'success', 'error');
            msg.textContent = '';
            msg.style.display = 'none'; // На всякий случай

            const formData = new FormData(form);
            // Показываем индикатор загрузки, если хотите
            // form.querySelector('.form-button').textContent = 'Отправка...';

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(r => {
                if (!r.ok) {
                    // Если HTTP статус не 2xx, считаем это ошибкой
                    throw new Error(`HTTP error! status: ${r.status}`);
                }
                return r.json();
            })
            .then(data => {
                // Показываем сообщение
                msg.textContent = data.message;
                if (data.success) {
                    msg.className = 'form-message success show'; // Успешное сообщение
                    form.reset(); // Очищаем форму только при успехе
                } else {
                    msg.className = 'form-message error show'; // Сообщение об ошибке
                }
                // Прокручиваем к сообщению
                msg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            })
            .catch(error => {
                // Ловим любые ошибки (сетевые, JSON.parse, etc.)
                console.error('Ошибка отправки:', error);
                msg.textContent = 'Ошибка отправки. Проверьте подключение и попробуйте позже.';
                msg.className = 'form-message error show';
                msg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            })
            .finally(() => {
                // Восстанавливаем текст кнопки, если меняли его
                // form.querySelector('.form-button').textContent = 'Отправить сообщение';
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const modalImg = document.getElementById("modal-img");
    const modalCaption = document.getElementById("modal-caption");
    const modalClose = document.querySelector(".modal-close");
    const modalPrev = document.querySelector(".modal-prev");
    const modalNext = document.querySelector(".modal-next");

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
    }

    // При клике на маленькую картинку открываем модал с ней
    galleryImages.forEach((img, index) => {
        img.addEventListener("click", () => {
            modal.style.display = "flex";
            showImage(index);
        });
    });

    // Закрыть модал
    modalClose.onclick = () => {
        modal.style.display = "none";
    };

    // Навигация вперед
    modalNext.onclick = (e) => {
        e.stopPropagation();
        showImage(currentIndex + 1);
    };

    // Навигация назад
    modalPrev.onclick = (e) => {
        e.stopPropagation();
        showImage(currentIndex - 1);
    };

    // Закрытие по клику вне картинки
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    };

    // Опционально: стрелки на клавиатуре
    document.addEventListener("keydown", (e) => {
        if (modal.style.display === "flex") {
            if (e.key === "ArrowLeft") {
                showImage(currentIndex - 1);
            } else if (e.key === "ArrowRight") {
                showImage(currentIndex + 1);
            } else if (e.key === "Escape") {
                modal.style.display = "none";
            }
        }
    });
});
