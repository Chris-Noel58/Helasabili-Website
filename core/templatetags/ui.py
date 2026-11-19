"""UI helpers for the public site: SVG icons and responsive image thumbnails."""
import logging
import posixpath
import re
import time
from functools import lru_cache
from io import BytesIO

import os

from django import template
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.templatetags.static import static
from django.utils.html import format_html

logger = logging.getLogger(__name__)
register = template.Library()

THUMB_ROOT = 'thumbs'
THUMB_WIDTHS = (480, 800, 1200, 1600)
_ICON_NAME = re.compile(r'^[a-z0-9-]+$')

# Per-process memo: source name -> (urls by width, one thumbnail path to re-check, time).
# Failures are retried after a few minutes (e.g. an image uploaded after a failed attempt).
_thumb_memo = {}
_RETRY_FAILED_AFTER = 300


@lru_cache(maxsize=1)
def _sprite_url():
    return asset('img/icons.svg')


@register.simple_tag
def asset(path):
    """Static URL that changes whenever the file changes.

    In production ManifestStaticFilesStorage already puts a content hash in the name.
    In development we append the file's modification time so browsers never keep a
    stale stylesheet or script after an edit.
    """
    url = static(path)
    if settings.DEBUG:
        from django.contrib.staticfiles import finders
        found = finders.find(path)
        if found:
            url += '?v=%d' % int(os.path.getmtime(found))
    return url


@register.simple_tag
def icon(name, css_class='', label=''):
    """Render an icon from the static SVG sprite: {% icon "phone" %}."""
    if not _ICON_NAME.match(str(name)):
        return ''
    classes = f'icon {css_class}'.strip()
    if label:
        return format_html(
            '<svg class="{}" role="img" aria-label="{}"><use href="{}#i-{}"></use></svg>',
            classes, label, _sprite_url(), name,
        )
    return format_html(
        '<svg class="{}" aria-hidden="true" focusable="false"><use href="{}#i-{}"></use></svg>',
        classes, _sprite_url(), name,
    )


def _thumb_name(source_name, width):
    # Keep the original file name inside the thumbnail path so it stays recognisable.
    return posixpath.join(THUMB_ROOT, f'{source_name}.w{width}.webp')


def _generate_thumbs(field_file, widths):
    """Create any missing WebP thumbnails for ``field_file``. Returns {width: name}."""
    from PIL import Image, ImageOps

    source_name = field_file.name
    wanted = {w: _thumb_name(source_name, w) for w in widths}
    missing = {w: n for w, n in wanted.items() if not default_storage.exists(n)}
    if not missing:
        return wanted

    with field_file.storage.open(source_name, 'rb') as handle:
        with Image.open(handle) as original:
            original = ImageOps.exif_transpose(original)
            if original.mode not in ('RGB', 'RGBA'):
                original = original.convert('RGBA' if 'A' in original.getbands() else 'RGB')
            for width, name in sorted(missing.items()):
                copy = original.copy()
                copy.thumbnail((width, width * 3), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                copy.save(buffer, 'WEBP', quality=78, method=4)
                saved = default_storage.save(name, ContentFile(buffer.getvalue()))
                wanted[width] = saved
    return wanted


def _thumbs_for(field_file):
    """Return {width: url} for an image field, or {} if thumbnails are unavailable."""
    name = getattr(field_file, 'name', '')
    if not name:
        return {}
    cached = _thumb_memo.get(name)
    if cached is not None:
        result, probe, checked_at = cached
        if result:
            # Thumbnails can disappear (media/thumbs cleared, redeploy, another server).
            # One cheap existence check keeps us from ever serving a broken URL.
            if default_storage.exists(probe):
                return result
        elif time.monotonic() - checked_at < _RETRY_FAILED_AFTER:
            return result
    probe = ''
    try:
        names = _generate_thumbs(field_file, THUMB_WIDTHS)
        result = {w: default_storage.url(n) for w, n in names.items()}
        probe = names[max(names)]
    except Exception as exc:  # missing file, unsupported format, storage error
        logger.debug('Thumbnail generation skipped for %s: %s', name, exc)
        result = {}
    _thumb_memo[name] = (result, probe, time.monotonic())
    return result


@register.filter
def thumb(field_file, width=800):
    """URL of a resized WebP copy, falling back to the original image URL."""
    try:
        width = int(width)
    except (TypeError, ValueError):
        width = 800
    thumbs = _thumbs_for(field_file)
    if thumbs:
        best = min((w for w in thumbs if w >= width), default=max(thumbs))
        return thumbs[best]
    try:
        return field_file.url
    except Exception:
        return ''


@register.filter
def srcset(field_file, max_width=1600):
    """A srcset string of WebP thumbnails up to ``max_width``, or '' if unavailable."""
    try:
        max_width = int(max_width)
    except (TypeError, ValueError):
        max_width = 1600
    thumbs = _thumbs_for(field_file)
    return ', '.join(f'{url} {w}w' for w, url in sorted(thumbs.items()) if w <= max_width)


@register.filter
def whatsapp_number(value):
    """Normalise a Kenyan phone number to wa.me format (2547XXXXXXXX)."""
    digits = re.sub(r'\D', '', str(value or ''))
    if len(digits) == 10 and digits.startswith('0'):
        digits = '254' + digits[1:]
    elif len(digits) == 9:
        digits = '254' + digits
    return digits
