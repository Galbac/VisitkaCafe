document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('showReviewFormBtn');
    const container = document.getElementById('reviewFormContainer');

    if (btn && container) {
        btn.addEventListener('click', function () {
            if (container.style.display === 'none' || !container.style.display) {
                container.style.display = 'flex';
                btn.textContent = 'Скрыть форму';
                container.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                container.style.display = 'none';
                btn.textContent = 'Написать отзыв';
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

    // Лайтбокс для просмотра скриншотов отзывов
    const modal = document.getElementById('reviewImgModal');
    const modalImg = document.getElementById('reviewModalImg');
    const overlay = document.getElementById('reviewImgOverlay');
    const closeBtn = document.getElementById('reviewImgClose');

    if (modal && modalImg) {
        function openReviewModal(src) {
            modalImg.src = src;
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('show'), 10);
        }

        function closeReviewModal() {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
                modalImg.src = '';
            }, 300);
        }

        document.querySelectorAll('.review-image').forEach(img => {
            img.addEventListener('click', () => {
                openReviewModal(img.src);
            });
        });

        if (closeBtn) closeBtn.addEventListener('click', closeReviewModal);
        if (overlay) overlay.addEventListener('click', closeReviewModal);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                closeReviewModal();
            }
        });
    }
});
