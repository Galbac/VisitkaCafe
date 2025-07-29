from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Product, Certificate, GalleryImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_preview', 'certificate_tag')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('image_tag', 'certificate_tag')

    # Делаем поля кликабельными в списке
    list_display_links = ('name', 'image_preview')

    def image_preview(self, obj):
        """
        Отображение миниатюры в списке объектов (list view).
        Компактная, стилизованная иконка.
        """
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); border: 1px solid #ddd;" title="{obj.name}">'
            )
        return mark_safe(
            '<div style="height: 40px; width: 40px; background-color: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd;" title="Нет изображения">'
            '<span style="color: #999; font-size: 16px;">—</span>'
            '</div>'
        )

    image_preview.short_description = 'Фото'

    # Примечание: allow_tags устарело, используем mark_safe

    def image_tag(self, obj):
        """
        Отображение полноразмерного изображения в форме редактирования (change form).
        """
        if obj.image:
            return mark_safe(
                f'<a href="{obj.image.url}" target="_blank" title="Открыть оригинал">'
                f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 100%; border-radius: 5px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); border: 1px solid #eee;">'
                f'</a>'
            )
        return "Нет изображения"

    image_tag.short_description = 'Изображение'

    def certificate_tag(self, obj):
        """
        Отображение ссылки на сертификат.
        """
        if obj.certificate:
            return mark_safe(
                f'<a href="{obj.certificate.url}" target="_blank" style="color: #1a73e8; text-decoration: none; font-weight: 500;">'
                f'📄 Открыть'
                f'</a>'
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
                f'<img src="{obj.image.url}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" title="{obj.name}">'
            )
        return "-"

    admin_image_preview.short_description = _('Изображение')

    def admin_image_tag(self, obj):
        """Отображение полноразмерного изображения в форме редактирования."""
        if obj.image:
            return mark_safe(
                f'<a href="{obj.image.url}" target="_blank" title="Открыть оригинал">'
                f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 100%; border-radius: 5px; border: 1px solid #eee; margin-top: 10px;">'
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
    list_editable = ('order', 'is_active') # Позволяет редактировать порядок и активность прямо в списке
    readonly_fields = ('admin_image_tag', 'uploaded_at') # Поле uploaded_at только для чтения

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('image', 'admin_image_tag', 'alt_text', 'order', 'is_active')
        }),
        (_('Дополнительно'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',) # Сворачиваем по умолчанию
        }),
    )

    def admin_image_preview(self, obj):
        """Отображение миниатюры в списке объектов."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" title="{obj.alt_text or obj.image.name}">'
            )
        return "-"
    admin_image_preview.short_description = _('Изображение')

    def admin_image_tag(self, obj):
        """Отображение полноразмерного изображения в форме редактирования."""
        if obj.image:
            return mark_safe(
                f'<a href="{obj.image.url}" target="_blank" title="Открыть оригинал">'
                f'<img src="{obj.image.url}" style="max-height: 300px; max-width: 100%; border-radius: 8px; border: 1px solid #eee; margin-top: 10px;">'
                f'</a>'
            )
        return "-"
    admin_image_tag.short_description = _('Превью изображения')