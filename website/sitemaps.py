"""Dynamic sitemap: public pages plus every active listing and published post."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.models import BlogPost, Course


class StaticPagesSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'

    pages = {
        'home': 1.0,
        'courses_list': 0.9,
        'about': 0.6,
        'blog_list': 0.6,
        'videos': 0.5,
        'gallery': 0.5,
        'testimonials': 0.5,
        'contact': 0.7,
    }

    def items(self):
        return list(self.pages)

    def location(self, item):
        return reverse(f'website:{item}')

    def priority(self, item):
        return self.pages[item]


class ListingSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Course.objects.filter(is_active=True).order_by('pk')

    def location(self, obj):
        return reverse('website:courses_detail', args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-pk')

    def location(self, obj):
        return reverse('website:blog_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'pages': StaticPagesSitemap,
    'listings': ListingSitemap,
    'blog': BlogSitemap,
}
