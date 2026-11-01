import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Certificate, ContactMessage, GalleryImage, OrderRequest, Product, Review


class DemoSeedTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.directory.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    @patch('main.views.send_telegram_notification')
    def test_seed_is_idempotent_preserves_edits_and_sends_no_messages(self, notification):
        call_command('seed_demo', stdout=StringIO())
        product = Product.objects.get(slug='demo-seed-pelmeni-beef')
        product.description = 'Owner edit'
        product.save()
        call_command('seed_demo', stdout=StringIO())
        product.refresh_from_db()
        self.assertEqual(product.description, 'Owner edit')
        for model, count in [(Product, 6), (GalleryImage, 2), (Review, 3),
                             (Certificate, 1), (ContactMessage, 1), (OrderRequest, 2)]:
            self.assertEqual(model.objects.count(), count)
        self.assertFalse(Certificate.objects.get().is_active)
        self.assertTrue(all('ТЕСТОВЫЙ ОТЗЫВ' in item.text for item in Review.objects.all()))
        notification.assert_not_called()
        self.assertContains(self.client.get('/'), 'Демо-витрина')

    def test_real_products_are_preserved_and_not_marked_as_demo(self):
        real = Product.objects.create(name='Настоящий товар', slug='real-preserved', description='Owner content', weight='500 г', composition='Подтверждённый состав', calories=100, proteins=10, fats=5, carbs=15)
        self.assertNotContains(self.client.get('/'), 'Демо-витрина')
        call_command('seed_demo', stdout=StringIO())
        real.refresh_from_db()
        self.assertEqual(real.description, 'Owner content')
        self.assertEqual(Product.objects.count(), 7)
        call_command('audit_uploads', stdout=StringIO())
