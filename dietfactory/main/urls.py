from django.urls import path

from .views import HomeView, ProductListView, ProductDetailView, ProductDetailJsonView, CertificateView, \
    SearchProductsView, ReviewsListView, ContactAjaxView, ManifestView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<slug:slug>/json/', ProductDetailJsonView.as_view(), name='product_detail_json'),
    path('certifications/', CertificateView.as_view(), name='certifications'),
    path('search/', SearchProductsView.as_view(), name='search'),
    path('privacy/', HomeView.as_view(), name='privacy'),
    path('terms/', HomeView.as_view(), name='terms'),
    path('contact/', ContactAjaxView.as_view(), name='contact_ajax'),
    path('reviews/', ReviewsListView.as_view(), name='reviews_list'),
    path('manifest.json', ManifestView.as_view(), name='manifest'),
]
