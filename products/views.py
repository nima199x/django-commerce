from django.shortcuts import render
from .models import Category


def category_list(request):
    # فقط دسته‌هایی که والد ندارند را می‌گیریم
    categories = Category.objects.filter(parent=None, is_active=True)

    return render(request, 'products/category.html', {'categories': categories})
# Create your views here.
