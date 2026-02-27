from django.shortcuts import render
from products.models import Category  # مدل دسته بندی را ایمپورت کنید


def home_page(request):
    # گرفتن دسته‌بندی‌های اصلی (بدون فرزند)
    main_categories = Category.objects.filter(level=0)

    context = {
        'main_categories': main_categories,
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