from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # ۱. لیست دسته‌بندی‌ها
    path('categories/', views.category_list, name='category_list'),

    # ۲. دسته‌بندی اصلی (بدون والد)
    path('categories/<slug:parent_slug>/', views.category_products, name='category'),

    # ۳. دسته فرزند (والد/فرزند) -> این مسیر کلید حل مشکل است!
    path('categories/<slug:parent_slug>/<slug:child_slug>/', views.category_products, name='category_detail'),
]