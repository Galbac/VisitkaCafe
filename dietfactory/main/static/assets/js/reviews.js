document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('showReviewFormBtn');
    const container = document.getElementById('reviewFormContainer');

    btn.addEventListener('click', function () {
        if (container.style.display === 'none') {
            container.style.display = 'flex';
            btn.textContent = 'Скрыть форму';
            // Прокрутка к форме
            container.scrollIntoView({behavior: 'smooth', block: 'center'});
        } else {
            container.style.display = 'none';
            btn.textContent = 'Написать отзыв';
            // Прокрутка к кнопке
            btn.scrollIntoView({behavior: 'smooth', block: 'center'});
        }
    });
});