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
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('faqs/', views.faq_page, name='faq'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
]