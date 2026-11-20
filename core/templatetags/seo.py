"""Search-engine helpers: canonical URLs and schema.org JSON-LD blocks.

The JSON-LD is built in Python (not hand-written in templates) so it is always
valid JSON and safely escaped inside <script>. Test any page with
https://search.google.com/test/rich-results
"""
import json

from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from .ui import thumb

register = template.Library()

ORG_NAME = 'Helasabili Mobile Capital Ltd'

# Same escaping Django's json_script uses, so content can never close the <script>.
_JSON_ESCAPES = {ord('>'): '\\u003E', ord('<'): '\\u003C', ord('&'): '\\u0026'}


def _ld(data):
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).translate(_JSON_ESCAPES)
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')


def _origin(request):
    # Production is HTTPS-only; behind a proxy request.scheme can read "http".
    scheme = request.scheme if settings.DEBUG else 'https'
    return f'{scheme}://{request.get_host()}'


def _abs(request, url):
    if not url:
        return ''
    if url.startswith(('http://', 'https://')):
        return url
    return _origin(request) + url


def _text(value, limit=500):
    text = ' '.join(strip_tags(value or '').split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + '…'


def _image(request, field_file, width=1200):
    if not field_file:
        return ''
    return _abs(request, thumb(field_file, width))


def _org_ref(request):
    return {'@id': _origin(request) + '/#organization'}


@register.simple_tag(takes_context=True)
def canonical_url(context):
    """Absolute URL of this page without query string (?search=, utm_ tags...).

    Pagination is kept: page 2 of a list is its own page for Google.
    """
    request = context['request']
    url = _origin(request) + request.path
    page = request.GET.get('page', '')
    if page.isdigit() and int(page) > 1:
        url += f'?page={int(page)}'
    return url


@register.simple_tag(takes_context=True)
def site_jsonld(context):
    """The business (shown in Google's local/knowledge panel) and the website."""
    request = context['request']
    origin = _origin(request)
    info = context.get('contact_info')
    site_settings = context.get('site_settings')

    org = {
        '@type': 'RealEstateAgent',
        '@id': origin + '/#organization',
        'name': ORG_NAME,
        'url': origin + '/',
        'description': 'Verified land plots and secure property investments in Nakuru and Nanyuki, Kenya.',
        'areaServed': ['Nakuru', 'Nanyuki', 'Kenya'],
    }
    logo = ''
    if site_settings and site_settings.logo:
        logo = _image(request, site_settings.logo, 480)
    if logo:
        org['logo'] = logo
        org['image'] = logo
    if info:
        if info.phone_primary:
            org['telephone'] = info.phone_primary
        if info.email:
            org['email'] = info.email
        if info.address or info.city:
            country = (info.country or '').strip()
            org['address'] = {
                '@type': 'PostalAddress',
                'streetAddress': _text(info.address, 200),
                'addressLocality': info.city,
                'postalCode': info.postal_code,
                'addressCountry': 'KE' if country.lower() in ('', 'kenya') else country,
            }
        if info.latitude is not None and info.longitude is not None:
            org['geo'] = {
                '@type': 'GeoCoordinates',
                'latitude': float(info.latitude),
                'longitude': float(info.longitude),
            }
        same_as = [u for u in (info.facebook, info.twitter, info.linkedin, info.instagram, info.youtube) if u]
        if same_as:
            org['sameAs'] = same_as

    website = {
        '@type': 'WebSite',
        '@id': origin + '/#website',
        'name': ORG_NAME,
        'url': origin + '/',
        'publisher': {'@id': org['@id']},
        # Lets Google show a search box for the site that searches listings.
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {
                '@type': 'EntryPoint',
                'urlTemplate': origin + reverse('website:courses_list') + '?search={search_term_string}',
            },
            'query-input': 'required name=search_term_string',
        },
    }
    return _ld({'@context': 'https://schema.org', '@graph': [org, website]})


@register.simple_tag(takes_context=True)
def listing_jsonld(context, course):
    """A plot listing: product with price (when set) plus breadcrumb trail."""
    request = context['request']
    origin = _origin(request)
    url = origin + reverse('website:courses_detail', args=[course.pk])
    graph = []

    product = {
        '@type': 'Product',
        '@id': url + '#listing',
        'name': course.title,
        'url': url,
        'category': 'Land for sale',
        'brand': {'@type': 'Brand', 'name': ORG_NAME},
        'description': _text(course.description) or f'{course.title} by {ORG_NAME}.',
    }
    images = [_image(request, course.featured_image)]
    images += [_image(request, img.image) for img in context.get('gallery_images') or [] if getattr(img, 'image', None)][:5]
    images = [i for i in images if i]
    if images:
        product['image'] = images
    props = []
    if course.location:
        props.append({'@type': 'PropertyValue', 'name': 'Location', 'value': course.location})
    if course.plot_size:
        props.append({'@type': 'PropertyValue', 'name': 'Plot size', 'value': course.plot_size})
    if props:
        product['additionalProperty'] = props
    # Google only accepts a Product with an offer; unpriced listings ("On request")
    # get just the breadcrumb rather than markup Search Console would flag.
    if course.fees:
        product['offers'] = {
            '@type': 'Offer',
            'url': url,
            'price': f'{course.fees:.0f}',
            'priceCurrency': 'KES',
            'availability': 'https://schema.org/InStock',
            'seller': _org_ref(request),
        }
        graph.append(product)

    graph.append({
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': origin + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Properties', 'item': origin + reverse('website:courses_list')},
            {'@type': 'ListItem', 'position': 3, 'name': course.title, 'item': url},
        ],
    })
    return _ld({'@context': 'https://schema.org', '@graph': graph})


@register.simple_tag(takes_context=True)
def article_jsonld(context, post):
    """A news/blog post (eligible for article rich results)."""
    request = context['request']
    origin = _origin(request)
    url = origin + reverse('website:blog_detail', args=[post.slug])
    author_name = (post.author or '').strip()
    if author_name and author_name.lower() not in ('admin', 'administrator'):
        author = {'@type': 'Person', 'name': author_name}
    else:
        author = {'@type': 'Organization', 'name': ORG_NAME, 'url': origin + '/'}

    article = {
        '@type': 'BlogPosting',
        'headline': post.title[:110],
        'url': url,
        'mainEntityOfPage': url,
        'datePublished': post.published_date.isoformat(),
        'dateModified': post.updated_at.isoformat(),
        'author': author,
        'publisher': _org_ref(request),
    }
    if post.excerpt:
        article['description'] = _text(post.excerpt, 300)
    image = _image(request, post.featured_image)
    if image:
        article['image'] = [image]
    graph = [article, {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': origin + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'News', 'item': origin + reverse('website:blog_list')},
            {'@type': 'ListItem', 'position': 3, 'name': post.title, 'item': url},
        ],
    }]
    return _ld({'@context': 'https://schema.org', '@graph': graph})


@register.simple_tag(takes_context=True)
def videos_jsonld(context, videos, limit=None):
    """VideoObject per YouTube video, so the page can appear in Google video results."""
    items = list(videos or [])
    if limit:
        items = items[: int(limit)]
    graph = []
    for video in items:
        vid = video.youtube_id()
        if not vid:
            continue
        graph.append({
            '@type': 'VideoObject',
            'name': video.title,
            'description': _text(video.description) or video.title,
            'thumbnailUrl': [video.thumbnail or f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'],
            'uploadDate': video.created_at.isoformat(),
            'embedUrl': f'https://www.youtube.com/embed/{vid}',
            'url': f'https://www.youtube.com/watch?v={vid}',
        })
    if not graph:
        return ''
    return _ld({'@context': 'https://schema.org', '@graph': graph})


@register.simple_tag(takes_context=True)
def default_share_image(context):
    """Fallback og:image (site logo) for pages that don't set their own."""
    site_settings = context.get('site_settings')
    if site_settings and site_settings.logo:
        return _image(context['request'], site_settings.logo, 1200)
    return ''
