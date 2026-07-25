from django.shortcuts import render
from django.db.models import Q, Sum
from products.models import Category, Product


def home_page(request):
    main_categories = Category.objects.filter(level=0)

    # A product counts as in-stock if it has no variants and stock>0,
    # OR it has variants and at least one variant has stock>0.
    in_stock_filter = Q(variants__isnull=True, stock__gt=0) | Q(variants__stock__gt=0)

    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).filter(in_stock_filter).distinct()[:6]

    categories_with_products = []
    for cat in main_categories:
        children = cat.get_children()
        children_with_products = []
        for child in children:
            products = Product.objects.filter(
                category=child,
                is_active=True
            ).filter(in_stock_filter).distinct()[:8]
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