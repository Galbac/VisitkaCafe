from .models import Product


def demo_content(request):
    return {'demo_catalog_active': Product.objects.filter(slug__startswith='demo-seed-').exists()}
