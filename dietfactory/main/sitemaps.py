from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'products', 'certifications', 'reviews_list', 'privacy', 'terms']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return Product.objects.all().order_by('id')

    def location(self, item):
        return reverse('product_detail', kwargs={'slug': item.slug})
