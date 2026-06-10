from django.shortcuts import render
from products.models import Category, Product


def home_page(request):
    main_categories = Category.objects.filter(level=0)
    featured_products = Product.objects.filter(is_active=True)[:6]

    context = {
        'main_categories': main_categories,
        'featured_products': featured_products,
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