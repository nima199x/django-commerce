from django.shortcuts import render
from products.models import Category, Product


def home_page(request):
    main_categories = Category.objects.filter(level=0)
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]

    categories_with_products = []
    for cat in main_categories:
        children = cat.get_children()
        children_with_products = []
        for child in children:
            products = Product.objects.filter(
                category=child,
                is_active=True
            )[:8]
            if products:
                children_with_products.append({
                    'child': child,
                    'products': products,
                })
        if children_with_products:
            categories_with_products.append({
                'category': cat,
                'children_with_products': children_with_products,
            })

    context = {
        'main_categories': main_categories,
        'featured_products': featured_products,
        'categories_with_products': categories_with_products,
    }
    return render(request, 'home_page.html', context)


def contact_us(request):
    return render(request, 'contact_us.html', {})


def about_us(request):
    return render(request, 'about_us.html', {})


def category(request):
    return render(request, 'category.html', {})


def custom_404(request, exception):
    return render(request, '404.html', status=404)