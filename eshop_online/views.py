from django.shortcuts import render
from products.models import Category  # ۱. مدل را اینجا ایمپورت کن


def home_page(request):
    # ۲. تمام دسته‌های اصلی (آن‌هایی که والد ندارند) را از دیتابیس بگیر
    categories = Category.objects.filter(parent=None)

    context = {
        'categories': categories  # ۳. لیست را به قالب بفرست
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

#Auth Section

#Auth Section