document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("imgModal");
    if (!modal) return;

    const modalImg = document.getElementById("modalImg");
    const modalCaption = document.getElementById("modalCaption");
    const closeBtn = modal.querySelector(".modal-close");
    const prevBtn = modal.querySelector(".modal-prev");
    const nextBtn = modal.querySelector(".modal-next");

    const certItems = Array.from(document.querySelectorAll(".cert-item"));
    let currentIndex = 0;
    let lastFocused = null;

    function openModal(index) {
        const item = certItems[index];
        const img = item.querySelector(".cert-img");
        const name = item.querySelector(".cert-name").textContent;
        const desc = item.querySelector(".cert-desc").textContent;

        if (!img) return;
        if (!modal.classList.contains("show")) lastFocused = document.activeElement;
        modalImg.src = img.src;
        document.getElementById("certificateOriginal").href = img.src;
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        modalImg.alt = img.alt;
        modalCaption.textContent = `${name}: ${desc}`;
        currentIndex = index;

        // Используем таймер для плавного появления
        modal.style.display = "block";
        closeBtn.focus();
        setTimeout(() => {
            modal.classList.add("show");
        }, 10);
    }

    function closeModal() {
        modal.classList.remove("show");
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        lastFocused?.focus();
        setTimeout(() => {
            modal.style.display = "none";
        }, 300); // Должно совпадать с длительностью transition
    }

    // Открытие модального окна при клике на карточку
    certItems.forEach((item, index) => {
        const imgWrapper = item.querySelector(".cert-image-wrapper");
        imgWrapper.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openModal(index); }
        });
        item.querySelector(".cert-view-button")?.addEventListener("click", () => openModal(index));
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
            if (e.key === "Tab") {
                const elements = [...modal.querySelectorAll('button, a[href]')];
                const first = elements[0], last = elements[elements.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            }
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