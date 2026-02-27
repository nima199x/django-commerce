from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def category_list(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'products/category.html', {'categories': categories})


def category_products(request, parent_slug, child_slug=None):
    # ۱. اگر child_slug وجود داشت، یعنی آدرس دو مرحله‌ای است (والد/فرزند)
    if child_slug:
        # پیدا کردن فرزند با توجه به اسلاگ والد و فرزند (کل مسیر)
        category = get_object_or_404(
            Category,
            slug=child_slug,
            parent__slug=parent_slug
        )
    # ۲. اگر child_slug وجود نداشت، یعنی فقط دسته اصلی (ریشه) است
    else:
        category = get_object_or_404(Category, slug=parent_slug)

    # گرفتن محصولات (با استفاده از MPTT برای گرفتن محصولات زیرمجموعه‌ها)
    products = Product.objects.filter(
        category__in=category.get_descendants(include_self=True)
    )

    return render(request, 'products/category.html', {
        'category': category,
        'products': products
    })

def category_menu(request, slug):
    category = get_object_or_404(Category, slug=slug)


def category(request):
    context = {}
    return render(request, 'category.html', context)
