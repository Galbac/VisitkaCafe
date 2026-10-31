"""Validate uploads by content, with bounded reads and XML without entities."""
import re
from pathlib import Path

from defusedxml import ElementTree
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000


def validate_image_upload(value):
    if value.size > MAX_UPLOAD_BYTES:
        raise ValidationError('Максимальный размер изображения — 10 МБ.')
    formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}
    expected_format = formats.get(Path(value.name).suffix.lower())
    if not expected_format:
        raise ValidationError('Разрешены расширения JPEG, PNG и WebP.')
    position = value.tell()
    try:
        value.seek(0)
        with Image.open(value) as image:
            if image.format != expected_format:
                raise ValidationError('Разрешены изображения JPEG, PNG и WebP.')
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValidationError('Изображение не должно превышать 16 мегапикселей.')
            image.verify()
    except (OSError, ValueError, SyntaxError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValidationError('Некорректное изображение.') from exc
    finally:
        value.seek(position)


def validate_certificate_upload(value):
    if value.size > MAX_UPLOAD_BYTES:
        raise ValidationError('Максимальный размер сертификата — 10 МБ.')
    if Path(value.name).suffix.lower() != '.pdf':
        if Path(value.name).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
            raise ValidationError('Разрешены PDF, JPEG, PNG и WebP.')
        return validate_image_upload(value)
    position = value.tell()
    try:
        value.seek(0)
        if not value.read(8).startswith(b'%PDF-'):
            raise ValidationError('Некорректный PDF.')
    finally:
        value.seek(position)


def validate_icon_upload(value):
    if Path(value.name).suffix.lower() == '.png':
        return validate_image_upload(value)
    if Path(value.name).suffix.lower() != '.svg' or value.size > 256 * 1024:
        raise ValidationError('Разрешены PNG и SVG до 256 КБ.')
    position = value.tell()
    tags = {'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline',
            'polygon', 'title', 'desc', 'defs', 'linearGradient', 'radialGradient',
            'stop', 'clipPath'}
    attributes = {'width', 'height', 'viewBox', 'version', 'id', 'fill', 'fill-rule',
                  'fill-opacity', 'stroke', 'stroke-width', 'stroke-linecap',
                  'stroke-linejoin', 'stroke-opacity', 'stroke-dasharray', 'opacity',
                  'd', 'x', 'y', 'x1', 'x2', 'y1', 'y2', 'cx', 'cy', 'r', 'rx', 'ry',
                  'points', 'transform', 'offset', 'stop-color', 'stop-opacity',
                  'gradientUnits', 'gradientTransform', 'clip-path', 'clip-rule',
                  'preserveAspectRatio'}
    try:
        value.seek(0)
        raw = value.read(256 * 1024 + 1)
        # Reject alternate encodings and processing instructions ignored by tree parsing.
        # Browsers can process xml-stylesheet outside the SVG tree.
        decoded = raw.decode('utf-8-sig')
        decoded = re.sub(r'^\s*<\?xml\s+[^?]*\?>', '', decoded, count=1)
        if '<?' in decoded or '\x00' in decoded:
            raise ValueError('SVG processing instructions are forbidden')
        root = ElementTree.fromstring(raw, forbid_dtd=True)
        if root.tag not in {'svg', '{http://www.w3.org/2000/svg}svg'}:
            raise ValueError('Not SVG')
        for node in root.iter():
            tag = node.tag.removeprefix('{http://www.w3.org/2000/svg}')
            if tag not in tags:
                raise ValueError('Unsupported SVG element')
            for name, content in node.attrib.items():
                if name not in attributes:
                    raise ValueError('Unsupported SVG attribute')
                # Only local paint/clip references; no CSS, external URLs or events.
                content = re.sub(r'url\(#[A-Za-z_][\w.-]*\)', '', content)
                if re.search(r'url|[<>"\';&]|javascript:|data:|https?:', content, re.I):
                    raise ValueError('Unsafe SVG attribute')
    except Exception as exc:
        raise ValidationError('SVG содержит неподдерживаемые или небезопасные элементы.') from exc
    finally:
        value.seek(position)
