from html import escape
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Product, Certificate, GalleryImage, Review, Exclusion, ContactMessage, OrderRequest


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'weight', 'image_preview', 'certificate_tag')
    search_fields = ('name', 'description', 'composition')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('image_tag', 'certificate_tag')
    list_display_links = ('name', 'image_preview')

    # Поля, которые будут отображаться в форме редактирования
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'slug', 'description', 'technology', 'image', 'image_tag']
        }),
        ('Состав и питание', {
            'fields': ['weight', 'composition', 'calories', 'proteins', 'fats', 'carbs'],
            'description': '<p style="color: #555; font-size: 0.9em;">Укажите состав и КБЖУ на 100 грамм продукта.</p>'
        }),
        ('Файлы', {
            'fields': ['certificate', 'certificate_tag']
        }),
        ('Ссылки', {
            'fields': ['instagram']
        }),
    ]

    # Отображение миниатюры в списке
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{escape(str(obj.image.url))}" '
                'style="height: 40px; width: 40px; object-fit: cover; border-radius: 5px; '
                'box-shadow: 0 1px 3px rgba(0,0,0,0.2); border: 1px solid #ddd;" '
                f'title="{escape(str(obj.name))}">'
            )
        return mark_safe(
            '<div style="height: 40px; width: 40px; background-color: #f0f0f0; '
            'border-radius: 5px; display: flex; align-items: center; justify-content: center; '
            'border: 1px solid #ddd;" title="Нет изображения">'
            '<span style="color: #999; font-size: 16px;">—</span></div>'
        )

    image_preview.short_description = 'Фото'

    # Отображение изображения в форме
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(
                f'<a href="{escape(str(obj.image.url))}" target="_blank" title="Открыть оригинал">'
                f'<img src="{escape(str(obj.image.url))}" style="max-height: 200px; max-width: 100%; '
                'border-radius: 5px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); '
                'border: 1px solid #eee;">'
                '</a>'
            )
        return "Нет изображения"

    image_tag.short_description = 'Изображение'

    # Отображение сертификата
    def certificate_tag(self, obj):
        if obj.certificate:
            return mark_safe(
                f'<a href="{escape(str(obj.certificate.url))}" target="_blank" style="color: #1a73e8; '
                'text-decoration: none; font-weight: 500;">📄 Открыть</a>'
            )
        return '-'

    certificate_tag.short_description = 'Сертификат'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Certificate в админке Django.
    """
    list_display = ('name', 'order', 'is_active', 'admin_image_preview')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')  # Позволяет редактировать порядок и активность прямо в списке
    readonly_fields = ('admin_image_tag',)  # Поле только для чтения для предпросмотра

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'description', 'order', 'is_active')
        }),
        (_('Изображение'), {
            'fields': ('image', 'admin_image_tag'),
        }),
    )

    def admin_image_preview(self, obj):
        """Отображение миниатюры в списке объектов."""
        if obj.image:
            return mark_safe(
                f'<img src="{escape(str(obj.image.url))}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" title="{escape(str(obj.name))}">'
            )
        return "-"

    admin_image_preview.short_description = _('Изображение')

    def admin_image_tag(self, obj):
        """Отображение полноразмерного изображения в форме редактирования."""
        if obj.image:
            return mark_safe(
                f'<a href="{escape(str(obj.image.url))}" target="_blank" title="Открыть оригинал">'
                f'<img src="{escape(str(obj.image.url))}" style="max-height: 200px; max-width: 100%; border-radius: 5px; border: 1px solid #eee; margin-top: 10px;">'
                f'</a>'
            )
        return "-"

    admin_image_tag.short_description = _('Превью изображения')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели GalleryImage в админке Django.
    """
    list_display = ('admin_image_preview', 'alt_text', 'order', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('alt_text',)
    list_editable = ('order', 'is_active')  # Позволяет редактировать порядок и активность прямо в списке
    readonly_fields = ('admin_image_tag', 'uploaded_at')  # Поле uploaded_at только для чтения

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('image', 'admin_image_tag', 'alt_text', 'order', 'is_active')
        }),
        (_('Дополнительно'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)  # Сворачиваем по умолчанию
        }),
    )

    def admin_image_preview(self, obj):
        """Отображение миниатюры в списке объектов."""
        if obj.image:
            return mark_safe(
                f'<img src="{escape(str(obj.image.url))}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" title="{escape(str(obj.alt_text or obj.image.name))}">'
            )
        return "-"

    admin_image_preview.short_description = _('Изображение')

    def admin_image_tag(self, obj):
        """Отображение полноразмерного изображения в форме редактирования."""
        if obj.image:
            return mark_safe(
                f'<a href="{escape(str(obj.image.url))}" target="_blank" title="Открыть оригинал">'
                f'<img src="{escape(str(obj.image.url))}" style="max-height: 300px; max-width: 100%; border-radius: 8px; border: 1px solid #eee; margin-top: 10px;">'
                f'</a>'
            )
        return "-"

    admin_image_tag.short_description = _('Превью изображения')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_active', 'has_text', 'has_screenshot')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('name', 'text')
    readonly_fields = ('created_at',)

    def has_text(self, obj):
        return bool(obj.text)

    has_text.boolean = True
    has_text.short_description = "Есть текст"

    def has_screenshot(self, obj):
        return bool(obj.screenshot)

    has_screenshot.boolean = True
    has_screenshot.short_description = "Есть скриншот"


@admin.register(Exclusion)
class ExclusionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'icon_preview')
    list_editable = ('order',)
    list_display_links = ('name',)
    list_per_page = 20
    ordering = ['order']

    # Превью иконки в списке
    def icon_preview(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{escape(str(obj.icon.url))}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 8px;">')
        return '—'

    icon_preview.short_description = 'Превью'

    # Форма редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'icon', 'order')
        }),
    )

    search_fields = ['name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    list_editable = ('is_processed',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('customer_name', 'phone', 'comment')
    readonly_fields = ('created_at',)
