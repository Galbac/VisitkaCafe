import io
import json
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .forms import ReviewForm
from .models import OrderRequest
from .validators import validate_certificate_upload, validate_icon_upload, validate_image_upload


class UploadSecurityTests(TestCase):
    def test_valid_image_keeps_stream_position(self):
        content = io.BytesIO()
        Image.new('RGB', (2, 2)).save(content, format='PNG')
        upload = SimpleUploadedFile('image.png', content.getvalue())
        upload.seek(3)
        validate_image_upload(upload)
        self.assertEqual(upload.tell(), 3)

    def test_image_cannot_have_an_active_extension(self):
        content = io.BytesIO()
        Image.new('RGB', (2, 2)).save(content, format='PNG')
        with self.assertRaises(ValidationError):
            validate_image_upload(SimpleUploadedFile('image.html', content.getvalue()))

    def test_html_is_not_an_image_or_certificate(self):
        for name, validator in [('image.png', validate_image_upload),
                                ('certificate.pdf', validate_certificate_upload),
                                ('certificate.html', validate_certificate_upload)]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validator(SimpleUploadedFile(name, b'<script>alert(1)</script>'))

    def test_image_and_svg_size_limits(self):
        for name, validator in [('image.png', validate_image_upload), ('icon.svg', validate_icon_upload)]:
            upload = SimpleUploadedFile(name, b'invalid')
            upload.size = 11 * 1024 * 1024
            with self.assertRaises(ValidationError):
                validator(upload)

    def test_svg_rejects_active_content_and_external_resources(self):
        cases = [
            '<script>alert(1)</script>',
            '<image href="https://example.com/tracker"/>',
            '<path onload="alert(1)"/>',
            '<foreignObject><div>HTML</div></foreignObject>',
            '<path fill="url(https://example.com/image)"/>',
            '<style>path {fill:red}</style>',
        ]
        for inner in cases:
            with self.subTest(inner=inner), self.assertRaises(ValidationError):
                validate_icon_upload(SimpleUploadedFile('icon.svg', (
                    '<svg xmlns="http://www.w3.org/2000/svg">' + inner + '</svg>'
                ).encode()))
        with self.assertRaises(ValidationError):
            validate_icon_upload(SimpleUploadedFile('icon.svg', b'<?xml-stylesheet href="https://example.com/style.css"?><svg/>'))
        with self.assertRaises(ValidationError):
            validate_icon_upload(SimpleUploadedFile('icon.svg', b'<!DOCTYPE svg [<!ENTITY x "x">]><svg>&x;</svg>'))

    def test_simple_svg_is_allowed(self):
        validate_icon_upload(SimpleUploadedFile('icon.svg', b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0 L10 10" fill="#fff"/></svg>'))


class PublicRequestSecurityTests(TestCase):
    def test_nested_json_cannot_cause_server_error(self):
        for route in ['contact_ajax', 'order_ajax']:
            for field in ['name', 'email', 'quantity', 'product_id', 'product_slug']:
                for value in [{}, []]:
                    with self.subTest(route=route, field=field, value=value):
                        response = self.client.post(reverse(route), data=json.dumps({
                            'name': 'Customer', 'phone': '+79999999999', field: value,
                        }), content_type='application/json')
                        self.assertEqual(response.status_code, 400)
        self.assertEqual(OrderRequest.objects.count(), 0)

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        for route in ['contact_ajax', 'order_ajax', 'reviews_list']:
            self.assertEqual(client.post(reverse(route), {}).status_code, 403)

    def test_review_length_is_bounded(self):
        self.assertFalse(ReviewForm({'name': 'Customer', 'text': 'x' * 5001}).is_valid())

    @patch('main.views.requests.post')
    @patch('main.views.TELEGRAM_BOT_TOKEN', 'test-token')
    @patch('main.views.TELEGRAM_CHAT_ID', 'test-chat')
    def test_notifications_are_plain_text_and_bounded(self, post):
        from .views import send_telegram_notification
        send_telegram_notification('<b>Title</b> &lt;script&gt;' + 'x' * 5000)
        data = post.call_args.kwargs['data']
        self.assertNotIn('parse_mode', data)
        self.assertTrue(data['text'].startswith('Title <script>'))
        self.assertLessEqual(len(data['text']), 2000)

    def test_unknown_host_is_rejected(self):
        self.assertEqual(self.client.get('/', HTTP_HOST='attacker.invalid').status_code, 400)
