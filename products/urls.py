from django.urls import path
from . import views # بهتر است کل ویوز را ایمپورت کنی

app_name = 'products'

urlpatterns = [
    # ۱. صفحه‌ای که لیست همه دسته‌بندی‌ها را نشان می‌دهد
    path('categories/', views.category_list, name='category_list'),

    # ۲. صفحه‌ای که محصولات یک دسته‌بندی خاص را نشان می‌دهد (اصلاح شد)
    path('categories/<slug:slug>/', views.category_products, name='category'),
]