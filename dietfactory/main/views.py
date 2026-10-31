import json
import logging
from html import escape

import requests
from decouple import config
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .forms import ContactForm, ReviewForm, OrderForm
from .models import Product, Certificate, GalleryImage, Exclusion, Review, ContactMessage, OrderRequest

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_CHAT_ID = config('TELEGRAM_CHAT_ID', default='')


def send_telegram_notification(text: str) -> bool:
    """Безопасная отправка уведомления в Telegram без падения приложения."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram Bot Token или Chat ID не заданы в конфигурации.")
        return False

    try:
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(
            tg_url,
            data={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': text,
                'parse_mode': 'HTML',
            },
            timeout=8
        )
        if response.ok:
            return True
        logger.error(f"Ошибка ответа Telegram API: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        logger.error("Ошибка подключения к Telegram: %s", type(e).__name__)
        return False


class HomeView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_images'] = GalleryImage.objects.filter(is_active=True)
        context['exclusions'] = Exclusion.objects.all()
        return context


class SearchProductsView(ListView):
    model = Product
    template_name = 'main/partials/search_results.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        if not query:
            return Product.objects.none()

        variants = {query, query.lower(), query.capitalize(), query.upper()}
        q_filter = models.Q()
        for v in variants:
            q_filter |= models.Q(name__contains=v)
            q_filter |= models.Q(description__contains=v)
            q_filter |= models.Q(composition__contains=v)

        # Также стандартный icontains для PostgreSQL
        q_filter |= (
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(composition__icontains=query)
        )

        return Product.objects.filter(q_filter).distinct().order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '').strip()
        return context


class CertificateView(TemplateView):
    template_name = "main/partials/certificates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificates'] = Certificate.objects.filter(is_active=True)
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'main/products.html'
    context_object_name = 'products'
    paginate_by = 24


class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.exclude(pk=self.object.pk)[:4]
        context['exclusions'] = Exclusion.objects.all()
        return context


class ProductDetailJsonView(View):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

        data = {
            'id': product.pk,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'technology': product.technology or '',
            'image': product.image.url if product.image else '',
            'certificate': product.certificate.url if product.certificate else '',
            'instagram': product.instagram or '',
            'weight': product.weight,
            'composition': product.composition,
            'calories': float(product.calories) if product.calories is not None else 0.0,
            'proteins': float(product.proteins) if product.proteins is not None else 0.0,
            'fats': float(product.fats) if product.fats is not None else 0.0,
            'carbs': float(product.carbs) if product.carbs is not None else 0.0,
        }
        return JsonResponse(data)


class ContactAjaxView(View):
    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'success': False, 'message': 'Неверный формат данных.'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'success': False}, status=400)
        form = ContactForm(data)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 1. Всегда сохраняем заявку в базу данных (защита от потери лидов)
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # 2. Отправляем в Telegram
            tg_message = (
                f"📩 <b>Новое обращение с сайта</b>\n"
                f"<b>👤 Имя:</b> {escape(str(name))}\n"
                f"<b>📧 Email:</b> {escape(str(email))}\n"
                f"<b>📝 Тема:</b> {escape(str(subject))}\n"
                f"<b>💬 Сообщение:</b>\n{escape(str(message))}\n"
                f"-----------------------------------\n"
            )
            send_telegram_notification(tg_message)

            return JsonResponse({'success': True, 'message': 'Спасибо! Ваше сообщение принято и сохранено.'})
        else:
            return JsonResponse({'success': False, 'message': 'Пожалуйста, проверьте корректность заполнения полей.'}, status=400)


class OrderAjaxView(View):
    """Прием заказов и заявок на полуфабрикаты онлайн"""

    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'success': False, 'message': 'Неверный формат данных.'}, status=400)

        if not hasattr(data, 'get') or isinstance(data, list):
            return JsonResponse({'success': False}, status=400)
        customer_name = str(data.get('customer_name') or data.get('name') or '').strip()
        phone = str(data.get('phone') or '').strip()
        quantity_raw = data.get('quantity', 1)
        comment = str(data.get('comment') or '').strip()
        product_id = data.get('product_id')
        product_slug = data.get('product_slug')

        if not customer_name or not phone:
            return JsonResponse({'success': False, 'message': 'Укажите ваше имя и номер телефона.'}, status=400)

        payload = {
            'customer_name': customer_name, 'phone': phone,
            'quantity': quantity_raw, 'comment': comment,
            'product': product_id or '',
        }
        if product_slug and not product_id:
            payload['product'] = Product.objects.filter(slug=product_slug).values_list('pk', flat=True).first()
            if not payload['product']:
                return JsonResponse({'success': False}, status=400)
        form = OrderForm(payload)
        if not form.is_valid():
            return JsonResponse({'success': False, 'message': 'Проверьте поля заказа.'}, status=400)
        order = form.save()
        product = order.product
        quantity = order.quantity

        product_name = product.name if product else "Без указания конкретного товара"
        tg_text = (
            f"🛍 <b>НОВЫЙ ЗАКАЗ С САЙТА #{order.pk}</b>\n"
            f"<b>📦 Товар:</b> {escape(str(product_name))}\n"
            f"<b>🔢 Количество:</b> {quantity} шт.\n"
            f"<b>👤 Клиент:</b> {escape(str(customer_name))}\n"
            f"<b>📞 Телефон:</b> {escape(str(phone))}\n"
        )
        if comment:
            tg_text += f"<b>💬 Комментарий/Адрес:</b> {escape(str(comment))}\n"
        tg_text += "-----------------------------------"

        send_telegram_notification(tg_text)

        return JsonResponse({
            'success': True,
            'message': 'Ваш заказ успешно оформлен! Мы свяжемся с вами в течение 15 минут.'
        })


class ReviewsListView(View):
    """Страница со всеми отзывами и формой добавления"""

    def get(self, request):
        reviews = Review.objects.filter(is_active=True).order_by('-created_at')
        paginator = Paginator(reviews, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form = ReviewForm()

        return render(request, 'main/reviews.html', {
            'page_obj': page_obj,
            'form': form
        })

    def post(self, request):
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_active = False  # На модерацию
            review.save()

            # Уведомляем владельца в Telegram о новом отзыве
            tg_text = (
                f"⭐ <b>НОВЫЙ ОТЗЫВ НА САЙТЕ (на модерации)</b>\n"
                f"<b>👤 Автор:</b> {escape(str(review.name))}\n"
                f"<b>💬 Отзыв:</b>\n{escape(str(review.text))}\n"
                f"-----------------------------------\n"
                f"Одобрите в админке: /admin/main/review/{review.pk}/change/"
            )
            send_telegram_notification(tg_text)

            messages.success(request, "Спасибо за ваш отзыв! Он появится на сайте сразу после проверки модератором.")
            return redirect('reviews_list')
        else:
            messages.error(request, "Пожалуйста, проверьте правильность заполнения формы.")
            reviews = Review.objects.filter(is_active=True).order_by('-created_at')
            paginator = Paginator(reviews, 12)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'main/reviews.html', {
                'page_obj': page_obj,
                'form': form
            })


class PrivacyView(TemplateView):
    template_name = "main/privacy.html"


class TermsView(TemplateView):
    template_name = "main/terms.html"


class RobotsTxtView(View):
    def get(self, request):
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml\n"
        )
        return HttpResponse(content, content_type="text/plain; charset=utf-8")


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "ok", "service": "dietfactory"})


class ManifestView(View):
    def get(self, request):
        manifest = {
            "name": "Еда без вреда",
            "short_name": "ЕдаБезВреда",
            "description": "Натуральные продукты без вреда для здоровья",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#2ecc71",
            "icons": [
                {
                    "src": request.build_absolute_uri("/static/assets/img/android-touch-icon.png"),
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": request.build_absolute_uri("/static/assets/img/android-touch-icon.png"),
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        return JsonResponse(manifest)
