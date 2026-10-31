from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from main.models import Product, Certificate, GalleryImage, Review, Exclusion
from main.validators import validate_certificate_upload, validate_icon_upload, validate_image_upload


class Command(BaseCommand):
    help = 'Read-only validation of existing uploads; exits nonzero on unsafe or missing files.'

    def handle(self, *args, **options):
        checks = [(Product, 'image', validate_image_upload),
                  (Product, 'certificate', validate_certificate_upload),
                  (Certificate, 'image', validate_image_upload),
                  (GalleryImage, 'image', validate_image_upload),
                  (Review, 'screenshot', validate_image_upload),
                  (Exclusion, 'icon', validate_icon_upload)]
        total = failed = 0
        for model, field, validator in checks:
            for instance in model.objects.exclude(**{field: ''}).exclude(**{field: None}).iterator():
                upload = getattr(instance, field)
                total += 1
                try:
                    if not Path(upload.path).resolve().is_relative_to(Path(settings.MEDIA_ROOT).resolve()):
                        raise ValidationError('File is outside MEDIA_ROOT')
                    validator(upload)
                except (ValidationError, OSError, ValueError):
                    failed += 1
                    self.stderr.write(f'Invalid upload: {model.__name__} id={instance.pk}, field={field}')
                finally:
                    upload.close()
        self.stdout.write(f'Checked uploads: {total}; invalid: {failed}')
        if failed:
            raise CommandError('Unsafe or missing uploads found. Review and replace these files.')
