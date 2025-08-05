import json

import requests
from decouple import config  # или используйте getattr
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
# views.py
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .forms import ContactForm
from .forms import ReviewForm
from .models import Product, Certificate, GalleryImage, Exclusion
from .models import Review


# Create your views here.


class HomeView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем активные изображения галереи, отсортированные по полю order
        context['gallery_images'] = GalleryImage.objects.filter(is_active=True)
        context['exclusions'] = Exclusion.objects.all()
        # ... (другой контекст, если есть) ...
        return context


class SearchProductsView(ListView):
    model = Product
    template_name = 'main/partials/search_results.html'
    context_object_name = 'products'
    paginate_by = 25

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        if not query:
            return Product.objects.none()

        queryset_case_sensitive = Product.objects.filter(name__contains=query)
        queryset = Product.objects.filter(name__icontains=query)

        if not queryset.exists() and queryset_case_sensitive.exists():
            query_lower = query.lower()
            queryset_lower = Product.objects.annotate(
                name_lower=Lower('name')
            ).filter(name_lower__contains=query_lower)
            for p in queryset_lower:
                queryset = queryset_lower
        return queryset

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


class ContactAjaxView(View):
    def post(self, request, *args, **kwargs):
        print("=== Начало обработки POST запроса ===")
        print("Content-Type:", request.content_type)
        print("Raw body:", request.body)

        # Парсим JSON
        try:
            data = json.loads(request.body)
            print("Parsed data:", data)
        except json.JSONDecodeError:
            print("❌ Ошибка парсинга JSON")
            return JsonResponse({'success': False, 'message': 'Неверный формат данных.'}, status=400)

        form = ContactForm(data)  # ← Передаём data, не request.POST

        if form.is_valid():
            print("✅ Форма валидна")
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            email_body = (
                f"✉️ Новое сообщение с сайта\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Имя: {name}\n"
                f"📧 Email: {email}\n"
                f"📝 Тема: {subject}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💬 Сообщение:\n{message}"
            )
            print(f"📧 Отправляем на: {settings.EMAIL_ADMIN}")

            try:
                print("📩 Начинаем отправку email...")
                print(f"  SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                print(f"  USE_SSL: {settings.EMAIL_USE_SSL}")
                print(f"  FROM: {settings.DEFAULT_FROM_EMAIL}")
                print(f"  TO: {settings.EMAIL_ADMIN}")
                print(f"  Пароль загружен: {'да' if settings.EMAIL_HOST_PASSWORD else 'нет'}")

                send_mail(
                    subject=f"Сообщение с сайта: {subject}",
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_ADMIN],
                    fail_silently=False,
                )
                print("✅ Письмо успешно отправлено")
                return JsonResponse({'success': True, 'message': 'Спасибо! Ваше сообщение отправлено.'})

            except Exception as e:
                import traceback
                print(f"❌ Ошибка при отправке email: {type(e).__name__}: {e}")
                print("Полный трейсбэк:")
                traceback.print_exc()
                return JsonResponse({'success': False, 'message': 'Ошибка отправки. Попробуйте позже.'})
        else:
            print("❌ Форма невалидна. Ошибки:", form.errors)
            return JsonResponse({'success': False, 'message': 'Проверьте правильность заполнения формы.'})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ProductDetailJsonView(View):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        data = {
            'name': product.name,
            'description': product.description,
            'technology': product.technology,
            'image': product.image.url if product.image else '',
            'certificate': product.certificate.url if product.certificate else '',
            'instagram': product.instagram,
            'weight': product.weight,
            'composition': product.composition,
            'calories': float(product.calories),
            'proteins': float(product.proteins),
            'fats': float(product.fats),
            'carbs': float(product.carbs),
        }
        return JsonResponse(data)


class ReviewsListView(View):
    """Страница со всеми отзывами"""

    def get(self, request):
        reviews = Review.objects.all().order_by('-created_at')  # сортировка по дате
        paginator = Paginator(reviews, 12)  # 12 отзывов на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form = ReviewForm()

        return render(request, 'main/reviews.html', {
            'page_obj': page_obj,
            'form': form
        })

    def post(self, request):
        form = ReviewForm(request.POST)
        reviews = Review.objects.all().order_by('-created_at')
        paginator = Paginator(reviews, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if form.is_valid():
            review = form.save(commit=False)
            # Можно включить модерацию: review.is_published = False
            review.save()
            messages.success(request, "Спасибо за ваш отзыв! Он будет опубликован после проверки.")
            return redirect('reviews_list')
        else:
            messages.error(request, "Проверьте правильность заполнения формы.")
            return render(request, 'main/reviews.html', {
                'page_obj': page_obj,
                'form': form
            })
