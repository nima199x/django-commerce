from django.contrib import admin
from .models import Category, Product

# ثبت مدل دسته‌بندی
admin.site.register(Category)

# ثبت مدل محصول
admin.site.register(Product)
# Register your models here.
