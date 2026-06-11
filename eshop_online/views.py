from django.shortcuts import render
from products.models import Category, Product


def home_page(request):
    main_categories = Category.objects.filter(level=0)
    featured_products = Product.objects.filter(is_active=True)[:6]

    categories_with_products = []
    for cat in main_categories:
        products = Product.objects.filter(
            category__in=cat.get_descendants(include_self=True),
            is_active=True
        )[:8]
        categories_with_products.append({
            'category': cat,
            'products': products,
        })

    context = {
        'main_categories': main_categories,
        'featured_products': featured_products,
        'categories_with_products': categories_with_products,
    }
    return render(request, 'home_page.html', context)
def contact_us(request):
    context = {}
    return render(request, 'contact_us.html', context)

def about_us(request):
    context = {}
    return render(request, 'about_us.html', context)
def category(request):
    context = {}
    return render(request, 'category.html', context)
def custom_404(request, exception):
    return render(request, '404.html', status=404)

#Auth Section

#Auth Section