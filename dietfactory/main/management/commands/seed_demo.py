"""Explicitly labelled demo content; no credentials, real claims or notifications."""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import Certificate, ContactMessage, GalleryImage, OrderRequest, Product, Review

PREFIX = 'demo-seed-'
PRODUCTS = [
    ('pelmeni-beef', 'Пельмени с говядиной', 'Говядина\nЛук\nМука\nВода', 220, 12, 8, 25),
    ('pelmeni-chicken', 'Пельмени с курицей', 'Курица\nЛук\nМука\nВода', 190, 14, 5, 22),
    ('vareniki-potato', 'Вареники с картофелем', 'Картофель\nЛук\nМука\nВода', 160, 4, 3, 29),
    ('vareniki-cherry', 'Вареники с вишней', 'Вишня\nМука\nВода', 170, 3, 2, 35),
    ('kurze-cheese', 'Курзе с творогом', 'Творог\nМука\nВода', 180, 11, 5, 23),
    ('chudu-herbs', 'Чуду с зеленью', 'Зелень\nМука\nВода\nМасло', 200, 5, 7, 29),
]


class Command(BaseCommand):
    help = 'Add labelled demo products, gallery, reviews and admin examples without overwriting existing records.'

    @transaction.atomic
    def handle(self, *args, **options):
        assets = Path(settings.BASE_DIR) / 'main/static/assets/img'
        created = {}
        products = []
        for code, title, composition, calories, proteins, fats, carbs in PRODUCTS:
            product, new = Product.objects.get_or_create(slug=PREFIX + code, defaults={
                'name': title + ' (демо)',
                'description': 'Демонстрационный товар. Пример карточки «' + title + '». Состав, фасовка и КБЖУ условные; это не предложение к продаже. Фото — иллюстрация, замените его фотографией продукта.',
                'technology': 'Демо: здесь укажите подтверждённые технологию, условия хранения и способ приготовления.',
                'weight': '500 г — демонстрационный пример',
                'composition': 'ДЕМО: условный состав, не используйте для проверки аллергенов.\n' + composition,
                'calories': calories, 'proteins': proteins, 'fats': fats, 'carbs': carbs,
                'instagram': '',
            })
            if new:
                with (assets / 'hero-bg.jpg').open('rb') as stream:
                    product.image.save(PREFIX + code + '.jpg', File(stream), save=False)
                product.full_clean()
                product.save()
            products.append(product)
            created['products'] = created.get('products', 0) + int(new)

        for order, (image, label) in enumerate([
            ('hero-bg.jpg', 'Демо: иллюстрация подачи, замените фотографией своей продукции'),
            ('apple-touch-icon_180.png', 'Демо: логотип бренда, пример изображения для галереи'),
        ], 1):
            gallery, new = GalleryImage.objects.get_or_create(alt_text=label, defaults={'order': order, 'is_active': True})
            if new:
                with (assets / image).open('rb') as stream:
                    gallery.image.save(PREFIX + image, File(stream), save=False)
                gallery.full_clean()
                gallery.save()
            created['gallery'] = created.get('gallery', 0) + int(new)

        for number in range(1, 4):
            _, new = Review.objects.get_or_create(name=f'Демо-покупатель {number}', defaults={
                'text': 'ТЕСТОВЫЙ ОТЗЫВ — не отзыв реального покупателя. Так будет выглядеть опубликованный отзыв. Замените пример реальным сообщением с согласия автора.',
                'is_active': True,
            })
            created['reviews'] = created.get('reviews', 0) + int(new)

        certificate, new = Certificate.objects.get_or_create(name='ДЕМО: пример карточки документа', defaults={
            'description': 'Непубличный пример для администратора. Это не сертификат качества. Загрузите настоящий документ, измените название и описание и только затем включите публикацию.',
            'is_active': False, 'order': 999,
        })
        if new:
            with (assets / 'apple-touch-icon_180.png').open('rb') as stream:
                certificate.image.save(PREFIX + 'document-placeholder.png', File(stream), save=False)
            certificate.full_clean()
            certificate.save()
        created['unpublished_document_examples'] = int(new)

        _, new = ContactMessage.objects.get_or_create(email='demo-seed@example.com', subject='ДЕМО: вопрос о доставке', defaults={
            'name': 'Демо-покупатель',
            'message': 'Тестовое обращение для знакомства с админкой. Настоящий клиент его не отправлял; уведомления не рассылались.',
        })
        created['contact_messages'] = int(new)
        for number, status in [(1, 'new'), (2, 'completed')]:
            _, new = OrderRequest.objects.get_or_create(customer_name=f'ДЕМО: заказ {number}', phone=f'+7000000000{number}', defaults={
                'product': products[number - 1], 'quantity': number,
                'comment': 'Тестовая запись для администратора, не реальный заказ. Уведомления не рассылались.',
                'status': status,
            })
            created['order_examples'] = created.get('order_examples', 0) + int(new)
        self.stdout.write(self.style.SUCCESS(f'Demo records created: {created}'))
