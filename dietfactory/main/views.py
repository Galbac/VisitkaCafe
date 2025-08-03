import requests
from decouple import config
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .forms import ContactForm
from .forms import ReviewForm
from .models import Product, Certificate, GalleryImage
from .models import Review


# Create your views here.


class HomeView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем активные изображения галереи, отсортированные по полю order
        context['gallery_images'] = GalleryImage.objects.filter(is_active=True)
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
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Telegram логика
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', config('TELEGRAM_BOT_TOKEN', default=''))
            chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', config('TELEGRAM_CHAT_ID', default=''))

            # Красивое сообщение
            text = (
                "✉️ <b>Новое сообщение с сайта</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Имя:</b> {name}\n"
                f"📧 <b>Email:</b> {email}\n"
                f"📝 <b>Тема:</b> {subject}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💬 <b>Сообщение:</b>\n{message}"
            )

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }

            try:
                resp = requests.post(url, data=payload, timeout=5)
                if resp.status_code == 200:
                    return JsonResponse({'success': True, 'message': 'Спасибо! Ваше сообщение отправлено.'})
                else:
                    return JsonResponse({'success': False, 'message': 'Ошибка отправки. Попробуйте позже.'})
            except Exception:
                return JsonResponse({'success': False, 'message': 'Ошибка соединения с Telegram.'})
        else:
            return JsonResponse({'success': False, 'message': 'Проверьте правильность заполнения формы.'})


contact_ajax = csrf_exempt(ContactAjaxView.as_view())


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
