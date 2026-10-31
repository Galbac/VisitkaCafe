document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('productModal');
    const modalSpinner = document.getElementById('modalSpinner');
    const modalImg = document.getElementById('modalImg');
    const modalName = document.getElementById('modalName');
    const modalDesc = document.getElementById('modalDesc');
    const modalTech = document.getElementById('modalTech');
    const modalCert = document.getElementById('modalCert');
    const modalClose = document.querySelector('.modal-close');
    const modalOverlay = document.querySelector('.modal-overlay');
    const productCards = document.querySelectorAll('.product-card');

    function openModal() {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
    }

    function closeModal() {
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    }

    function showProductModal(data) {
        modalName.textContent = data.name;
        modalDesc.textContent = data.description;
        modalTech.textContent = data.technology ? 'Технология: ' + data.technology : '';
        document.getElementById('modalWeight').textContent = data.weight;

        const compositionList = document.getElementById('compositionList');
        compositionList.innerHTML = '';
        (data.composition || '').split('\n').forEach(ing => {
            if (ing.trim()) {
                const li = document.createElement('li');
                li.textContent = ing.trim();
                compositionList.appendChild(li);
            }
        });

        document.getElementById('modalCalories').textContent = `${data.calories} ккал`;
        document.getElementById('modalProteins').textContent = `${data.proteins} г`;
        document.getElementById('modalFats').textContent = `${data.fats} г`;
        document.getElementById('modalCarbs').textContent = `${data.carbs} г`;

        modalImg.src = data.image || '';
        modalImg.alt = data.name;
        document.querySelector('.modal-img-wrap').style.display = data.image ? 'block' : 'none';

        if (data.certificate) {
            const certificateLink = document.createElement('a');
            certificateLink.href = data.certificate;
            certificateLink.target = '_blank';
            certificateLink.rel = 'noopener noreferrer';
            certificateLink.className = 'cert-link';
            certificateLink.textContent = '📜 Сертификат качества';
            modalCert.replaceChildren(certificateLink);
            modalCert.style.display = 'block';
        } else {
            modalCert.style.display = 'none';
        }

        const detailLink = document.getElementById('modalDetailLink');
        if (detailLink) {
            detailLink.href = `/products/${data.slug}/`;
        }
        const waLink = document.getElementById('modalWaOrderLink');
        if (waLink) {
            waLink.href = `https://wa.me/79634001323?text=${encodeURIComponent('Здравствуйте! Хочу заказать «' + data.name + '»')}`;
        }

        openModal();
    }

    function showSpinner() {
        modalSpinner.style.display = 'flex';
        document.querySelectorAll('.modal-body > .modal-img-wrap, .modal-body > .modal-name, .modal-body > .modal-desc, .modal-tech, .modal-cert, .macro-block, .composition-block').forEach(el => {
            el.style.display = 'none';
        });
    }

    function hideSpinner() {
        modalSpinner.style.display = 'none';
        document.querySelectorAll('.modal-body > .modal-img-wrap, .modal-body > .modal-name, .modal-body > .modal-desc, .modal-tech, .modal-cert, .macro-block, .composition-block').forEach(el => {
            el.style.display = 'block';
        });
    }

    productCards.forEach(card => {
        card.addEventListener('click', function () {
            const slug = this.getAttribute('data-slug');
            if (!slug) return;
            showSpinner();
            openModal();
            fetch(`/products/${slug}/json/`)
                .then(response => response.json())
                .then(data => {
                    hideSpinner();
                    showProductModal(data);
                })
                .catch(() => {
                    hideSpinner();
                    modalName.textContent = 'Ошибка';
                    modalDesc.textContent = 'Не удалось загрузить данные.';
                    modalTech.innerHTML = '';
                    document.querySelector('.modal-img-wrap').style.display = 'none';
                    modalCert.style.display = 'none';
                });
        });

        card.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });

    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && modal.classList.contains('show')) closeModal();
    });
    document.querySelector('.modal-content').addEventListener('click', e => e.stopPropagation());
});