from django.shortcuts import render, get_object_or_404
from .models import Category


def category_list(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'products/category.html', {'categories': categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # فرض می‌کنیم نام مدل  Product است.
    from .models import Product
    products = Product.objects.filter(category=category)

    return render(request, 'products/category.html', {
        'category': category,
        'products': products
    })


def category_menu(request, slug):
    category = get_object_or_404(Category, slug=slug)


def category(request):
    context = {}
    return render(request, 'category.html', context)
