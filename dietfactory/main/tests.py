import json
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from main.models import Product, Certificate, GalleryImage, Review, Exclusion, ContactMessage, OrderRequest


class ProductModelAndDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Пельмени с говядиной",
            description="Вкусные домашние пельмени без глютена",
            weight="500 г (около 25 штук)",
            composition="Говядина высший сорт, рисовая мука, вода, соль, перец",
            calories=Decimal("195.50"),
            proteins=Decimal("12.40"),
            fats=Decimal("6.20"),
            carbs=Decimal("22.10"),
        )

    def test_cyrillic_slug_generation(self):
        """Проверка автоматической транслитерации кириллических названий в slug."""
        self.assertTrue(self.product.slug)
        self.assertIn("pelmeni", self.product.slug)

    def test_product_detail_view_success(self):
        """Проверка рендеринга страницы товара product_detail.html."""
        url = reverse('product_detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пельмени с говядиной")
        self.assertContains(response, "195")
        self.assertContains(response, "Быстрый заказ онлайн")

    def test_product_detail_json_view(self):
        """Проверка JSON-ручки для модального окна."""
        url = reverse('product_detail_json', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], "Пельмени с говядиной")
        self.assertEqual(data['calories'], 195.5)
        self.assertEqual(data['proteins'], 12.4)

    def test_product_list_view(self):
        """Проверка каталога товаров."""
        url = reverse('products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пельмени с говядиной")


class SearchProductsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.p1 = Product.objects.create(
            name="Курзе с творогом",
            description="Традиционное блюдо без глютена",
            weight="400 г",
            composition="Творог обезжиренный, мука рисовая",
            calories=Decimal("150"),
            proteins=Decimal("14"),
            fats=Decimal("3"),
            carbs=Decimal("18")
        )
        self.p2 = Product.objects.create(
            name="Чуду с зеленью",
            description="Свежая зелень и тонкое безглютеновое тесто",
            weight="300 г",
            composition="Шпинат, лук, кинза, мука кукурузная",
            calories=Decimal("120"),
            proteins=Decimal("5"),
            fats=Decimal("2"),
            carbs=Decimal("20")
        )

    def test_search_by_name(self):
        url = reverse('search') + '?query=курзе'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курзе с творогом")
        self.assertNotContains(response, "Чуду с зеленью")

    def test_search_by_composition(self):
        url = reverse('search') + '?query=шпинат'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Чуду с зеленью")

    def test_search_empty_query(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Начните поиск")


class ContactAndOrderAjaxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Вареники с вишней",
            description="Сочная вишня без сахара",
            weight="450 г",
            composition="Вишня, рисовая мука",
            calories=Decimal("130"),
            proteins=Decimal("3"),
            fats=Decimal("1"),
            carbs=Decimal("26")
        )

    @patch('main.views.send_telegram_notification')
    def test_contact_ajax_success_saves_to_db(self, mock_tg):
        mock_tg.return_value = True
        payload = {
            'name': 'Амина',
            'email': 'amina@example.com',
            'subject': 'Вопрос по доставке',
            'message': 'Доставляете ли в Каспийск?'
        }
        url = reverse('contact_ajax')
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Проверяем сохранение в базу данных
        msg = ContactMessage.objects.filter(email='amina@example.com').first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'Амина')
        self.assertEqual(msg.subject, 'Вопрос по доставке')
        mock_tg.assert_called_once()

    @patch('main.views.send_telegram_notification')
    def test_order_ajax_success(self, mock_tg):
        mock_tg.return_value = True
        payload = {
            'customer_name': 'Магомед',
            'phone': '+7 (963) 400-00-00',
            'quantity': 3,
            'comment': 'Ул. Ленина, д. 10, кв. 5',
            'product_id': self.product.pk
        }
        url = reverse('order_ajax')
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Проверяем сохранение заказа в базу
        order = OrderRequest.objects.filter(customer_name='Магомед').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, 3)
        self.assertEqual(order.product, self.product)
        mock_tg.assert_called_once()


class ReviewsModerationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_review = Review.objects.create(
            name="Хадижат",
            text="Очень вкусные пельмени!",
            is_active=True
        )
        self.inactive_review = Review.objects.create(
            name="Инкогнито",
            text="Спам-сообщение",
            is_active=False
        )

    def test_get_reviews_only_shows_active(self):
        url = reverse('reviews_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Хадижат")
        self.assertNotContains(response, "Спам-сообщение")

    @patch('main.views.send_telegram_notification')
    def test_post_review_saved_as_inactive(self, mock_tg):
        mock_tg.return_value = True
        url = reverse('reviews_list')
        post_data = {
            'name': 'Мурад',
            'text': 'Попробовал хинкал без глютена — супер!'
        }
        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что созданный отзыв не опубликован сразу
        new_rev = Review.objects.filter(name='Мурад').first()
        self.assertIsNotNone(new_rev)
        self.assertFalse(new_rev.is_active)
        mock_tg.assert_called_once()


class StaticAndLegalPagesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_page(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Политика конфиденциальности")

    def test_terms_page(self):
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользовательское соглашение")

    def test_health_check(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_robots_txt(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("User-agent: *", response.content.decode('utf-8'))

    def test_sitemap_xml(self):
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertIn('<urlset', response.content.decode('utf-8'))
