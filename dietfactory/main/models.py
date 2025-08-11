# models.py
import os
import tempfile

from PIL import Image
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# Универсальная функция удаления файла
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
                print(f"Файл {file_path} вне MEDIA_ROOT — не удаляется.")
        else:
            print(f"Файл {file_path} не существует на диске.")
    else:
        print("Поле файла пустое или не имеет атрибута path.")


# Функция оптимизации изображения
def optimize_image(image_field, max_size=(1200, 1200), quality=85):
    """
    Сжимает и уменьшает изображение.
    :param image_field: файл изображения
    :param max_size: максимальный размер (ширина, высота)
    :param quality: качество (1-100)
    :return: путь к временному оптимизированному файлу
    """
    if not image_field:
        return None

    img = Image.open(image_field)
    img_format = img.format  # Сохраняем формат (JPEG, PNG и т.д.)

    # Конвертируем PNG в RGB, если есть альфа-канал
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    # Уменьшаем, если слишком большое
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Сохраняем во временный файл
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file, format='JPEG', quality=quality, optimize=True)
    temp_file.close()

    return temp_file.name, img_format



class Product(models.Model):
    name = models.CharField('Название продукта', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание продукта')
    technology = models.TextField('Технология производства', blank=True)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    certificate = models.FileField('Сертификат', upload_to='certificates/', blank=True, null=True)
    instagram = models.URLField('Ссылка на Instagram', blank=True,
                                default='https://www.instagram.com/eda__bez.vreda?igsh=eHR2bjNoNjNmcnA4')

    weight = models.TextField('Вес / фасовка', help_text="Например: 300 г (2 штуки)")
    composition = models.TextField('Состав', help_text="Каждый ингредиент с новой строки")

    # КБЖУ на 100 грамм
    calories = models.PositiveSmallIntegerField('Калории (ккал)', help_text="на 100 г")
    proteins = models.DecimalField('Белки (г)', max_digits=4, decimal_places=1, help_text="на 100 г")
    fats = models.DecimalField('Жиры (г)', max_digits=4, decimal_places=1, help_text="на 100 г")
    carbs = models.DecimalField('Углеводы (г)', max_digits=4, decimal_places=1, help_text="на 100 г")

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = "product"
            slug = base_slug
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Certificate(models.Model):
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
        ordering = ['order']

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
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
        return self.alt_text or f"Изображение #{self.pk}"


class Review(models.Model):
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Текст отзыва", blank=True, null=True)
    screenshot = models.ImageField(
        "Скриншот из Instagram",
        upload_to='reviews/',
        blank=True,
        null=True,
        help_text="Можно загрузить скриншот отзыва из Instagram"
    )
    created_at = models.DateTimeField("Дата", default=timezone.now)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.created_at.strftime('%d.%m.%Y')}"



@receiver(pre_save, sender=Review)
def optimize_review_screenshot(sender, instance, **kwargs):
    if not instance.pk:  # Новый объект
        if instance.screenshot:
            temp_path, original_format = optimize_image(instance.screenshot)
            if temp_path:
                # Заменяем файл на оптимизированный
                from django.core.files import File
                with open(temp_path, 'rb') as f:
                    instance.screenshot.save(
                        instance.screenshot.name.split('.')[0] + '.jpg',
                        File(f),
                        save=False
                    )
                os.remove(temp_path)  # Удаляем временный файл
    else:
        # Объект уже существует — проверим, изменилось ли изображение
        try:
            old_instance = Review.objects.get(pk=instance.pk)
            if old_instance.screenshot and old_instance.screenshot != instance.screenshot:
                delete_file_if_exists(old_instance.screenshot)
        except Review.DoesNotExist:
            pass


@receiver(post_delete, sender=Review)
def delete_review_screenshot(sender, instance, **kwargs):
    if instance.screenshot:
        delete_file_if_exists(instance.screenshot)


class Exclusion(models.Model):
    name = models.CharField(
        'Название',
        max_length=50,
        help_text='Например: Сахара, Лактозы'
    )
    icon = models.ImageField(
        'Иконка',
        upload_to='exclusions/',
        help_text='SVG или PNG (рекомендуется 100x100)'
    )
    order = models.PositiveIntegerField(
        'Порядок',
        default=0,
        db_index=True,
        help_text='Меньше — выше в списке'
    )

    class Meta:
        verbose_name = 'Элемент "Не содержит"'
        verbose_name_plural = 'Элементы "Не содержит"'
        ordering = ['order']

    def __str__(self):
        return self.name
