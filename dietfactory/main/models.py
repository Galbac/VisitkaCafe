# Create your models here.
import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField('Название продукта')
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание продукта')
    technology = models.TextField('Технология производства', blank=True)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    certificate = models.FileField('Сертификат', upload_to='certificates/', blank=True, null=True)
    instagram = models.URLField('Ссылка на Instagram', blank=True,
                                default='https://www.instagram.com/eda__bez.vreda?igsh=eHR2bjNoNjNmcnA4')

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                # Если slugify не дал результата, используем ID или заглушку
                base_slug = "product"
            slug = base_slug
            n = 1
            # Используем try-except на случай гонки данных
            try:
                while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{n}"
                    n += 1
            except:
                # На случай ошибок с БД, добавляем временную метку
                import time
                slug = f"{base_slug}-{int(time.time())}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    """
    Модель для хранения информации о сертификатах качества.
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_("Название сертификата"),
        help_text=_("Например, ГОСТ Р 51074-2003, ISO 22000")
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        help_text=_("Краткое описание стандарта или сертификата")
    )
    image = models.ImageField(
        upload_to='certificates/',
        verbose_name=_("Изображение сертификата"),
        help_text=_("Файл изображения сертификата")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок"),
        help_text=_("Определяет порядок отображения сертификатов (меньше - выше)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
        help_text=_("Отметьте, чтобы сертификат отображался на сайте")
    )

    class Meta:
        verbose_name = _("Сертификат")
        verbose_name_plural = _("Сертификаты")
        ordering = ['order']  # Сортировка по полю order по возрастанию

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    """
    Модель для хранения изображений галереи.
    """
    image = models.ImageField(
        upload_to='gallery/',
        verbose_name=_("Изображение"),
        help_text=_("Файл изображения для галереи")
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Альтернативный текст (Alt)"),
        help_text=_("Описание изображения для SEO и доступности")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок"),
        help_text=_("Определяет порядок отображения изображений (меньше - выше)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активно"),
        help_text=_("Отметьте, чтобы изображение отображалось в галерее")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата загрузки")
    )

    class Meta:
        verbose_name = _("Изображение галереи")
        verbose_name_plural = _("Изображения галереи")
        ordering = ['order']

    def __str__(self):
        if self.alt_text:
            return self.alt_text
        return f"Изображение #{self.pk}"


def delete_file_if_exists(file_field):
    if file_field and hasattr(file_field, 'path'):
        file_path = file_field.path
        if os.path.isfile(file_path) and file_path.startswith(settings.MEDIA_ROOT):
            try:
                os.remove(file_path)
                print(f"Файл удален: {file_path}")
            except OSError as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")


def delete_file_if_exists(file_field):
    if file_field and hasattr(file_field, 'path'):
        file_path = file_field.path
        if os.path.isfile(file_path):
            media_root_str = str(settings.MEDIA_ROOT)
            if file_path.startswith(media_root_str):
                try:
                    os.remove(file_path)
                    print(f"Файл удален: {file_path}")
                except OSError as e:
                    print(f"Ошибка при удалении файла {file_path}: {e}")
            else:
                print(f"Файл {file_path} не будет удален, так как не находится внутри MEDIA_ROOT.")
        else:
            print(f"Файл {file_path} не существует на диске.")
    else:
        print("Поле файла пустое или не имеет атрибута path.")


@receiver(post_delete, sender=Product)
def delete_product_files(sender, instance, **kwargs):
    if instance.image:
        delete_file_if_exists(instance.image)
    if instance.certificate:
        delete_file_if_exists(instance.certificate)


@receiver(post_delete, sender=Certificate)
def delete_certificate_image(sender, instance, **kwargs):
    if instance.image:
        delete_file_if_exists(instance.image)


@receiver(post_delete, sender=GalleryImage)
def delete_gallery_image(sender, instance, **kwargs):
    if instance.image:
        delete_file_if_exists(instance.image)
