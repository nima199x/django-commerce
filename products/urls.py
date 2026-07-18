from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:parent_slug>/', views.category_products, name='category'),
    path('categories/<slug:parent_slug>/<slug:child_slug>/', views.category_products, name='category_detail'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('faqs/', views.faq_page, name='faq'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('reviews/submit/<int:order_item_id>/', views.submit_review, name='submit_review'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
    path('specials/', views.specials, name='specials'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:item_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('compare/', views.compare_detail, name='compare_detail'),
    path('compare/add/<int:product_id>/', views.compare_add, name='compare_add'),
    path('compare/remove/<int:product_id>/', views.compare_remove, name='compare_remove'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),

]