from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .sitemaps import StaticViewSitemap, ProductSitemap
from .views import (
    HomeView,
    ProductListView,
    ProductDetailView,
    ProductDetailJsonView,
    CertificateView,
    SearchProductsView,
    ReviewsListView,
    ContactAjaxView,
    OrderAjaxView,
    PrivacyView,
    TermsView,
    RobotsTxtView,
    HealthCheckView,
    ManifestView,
)

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<slug:slug>/json/', ProductDetailJsonView.as_view(), name='product_detail_json'),
    path('certifications/', CertificateView.as_view(), name='certifications'),
    path('search/', SearchProductsView.as_view(), name='search'),
    path('order/', OrderAjaxView.as_view(), name='order_ajax'),
    path('contact/', ContactAjaxView.as_view(), name='contact_ajax'),
    path('reviews/', ReviewsListView.as_view(), name='reviews_list'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('manifest.json', ManifestView.as_view(), name='manifest'),
]
