document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("imgModal");
    const modalImg = document.getElementById("modalImg");
    const modalCaption = document.getElementById("modalCaption");
    const closeBtn = modal.querySelector(".modal-close");
    const prevBtn = modal.querySelector(".modal-prev");
    const nextBtn = modal.querySelector(".modal-next");

    const certItems = Array.from(document.querySelectorAll(".cert-item"));
    let currentIndex = 0;

    function openModal(index) {
        const item = certItems[index];
        const img = item.querySelector(".cert-img");
        const name = item.querySelector(".cert-name").textContent;
        const desc = item.querySelector(".cert-desc").textContent;

        modalImg.src = img.src;
        modalImg.alt = img.alt;
        modalCaption.textContent = `${name}: ${desc}`;
        currentIndex = index;

        // Используем таймер для плавного появления
        modal.style.display = "block";
        setTimeout(() => {
            modal.classList.add("show");
        }, 10);
    }

    function closeModal() {
        modal.classList.remove("show");
        setTimeout(() => {
            modal.style.display = "none";
        }, 300); // Должно совпадать с длительностью transition
    }

    // Открытие модального окна при клике на карточку
    certItems.forEach((item, index) => {
        const imgWrapper = item.querySelector(".cert-image-wrapper");
        imgWrapper.addEventListener("click", () => {
            openModal(index);
        });
    });

    // Закрытие модального окна
    closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Навигация стрелками
    function navigate(direction) {
        currentIndex += direction;
        if (currentIndex < 0) {
            currentIndex = certItems.length - 1;
        } else if (currentIndex >= certItems.length) {
            currentIndex = 0;
        }
        openModal(currentIndex);
    }

    prevBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        navigate(-1);
    });

    nextBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        navigate(1);
    });

    // Навигация клавишами
    document.addEventListener("keydown", (e) => {
        if (modal.classList.contains("show")) {
            if (e.key === "Escape") {
                closeModal();
            } else if (e.key === "ArrowLeft") {
                navigate(-1);
            } else if (e.key === "ArrowRight") {
                navigate(1);
            }
        }
    });
});