from .models import Category  # 📂 چون در همان پوشه هستی از نقطه استفاده می‌کنیم


def include_categories(request):
    # 🔍 فقط دسته‌هایی که والد ندارند (سرشاخه‌ها) را می‌گیریم
    categories = Category.objects.filter(parent=None, is_active=True)
    return {
        'categories': categories  # 🎁 این نام در تمام قالب‌ها در دسترس خواهد بود
    }


def cart_context(request):
    from .models import Cart
    cart = None
    if request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
    return {'cart': cart}


def sidebar_context(request):
    from .models import Product
    sidebar_products = Product.objects.filter(is_active=True)[:5]
    return {'sidebar_products': sidebar_products}


def banners_context(request):
    from .models import Banner, Slider, Brand
    return {
        'top_banners': Banner.objects.filter(position='top', is_active=True).order_by('order'),
        'middle_banners': Banner.objects.filter(position='middle', is_active=True).order_by('order'),
        'bottom_banners': Banner.objects.filter(position='bottom', is_active=True).order_by('order'),
        'side_banners': Banner.objects.filter(position='side', is_active=True).order_by('order'),
        'sliders': Slider.objects.filter(is_active=True).order_by('order'),
        'brands': Brand.objects.filter(is_active=True).order_by('order'),
    }
