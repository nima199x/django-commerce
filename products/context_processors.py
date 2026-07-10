from .models import Category, SiteSettings


def include_categories(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return {
        'categories': categories
    }


def cart_context(request):
    from .models import Cart
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key, user=None).first()
    return {'cart': cart}


def sidebar_context(request):
    from .models import Product
    from django.db.models import Sum, Q

    latest_products = Product.objects.filter(is_active=True).order_by('-id')[:5]
    special_products = Product.objects.filter(is_active=True, discount__gt=0).order_by('-discount')[:5]

    bestseller_products = Product.objects.filter(is_active=True).annotate(
        sales_count=Sum(
            'order_items__quantity',
            filter=Q(order_items__order__status='completed')
        )
    ).filter(sales_count__gt=0).order_by('-sales_count')[:5]

    return {
        'latest_products': latest_products,
        'special_products': special_products,
        'bestseller_products': bestseller_products,
    }


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


def wishlist_context(request):
    from .models import WishlistItem
    count = 0
    if request.user.is_authenticated:
        count = WishlistItem.objects.filter(user=request.user).count()
    return {'wishlist_count': count}


def compare_context(request):
    compare_list = request.session.get('compare_list', [])
    return {'compare_count': len(compare_list)}


def site_settings_context(request):
    from .models import SiteSettings
    return {'site_settings': SiteSettings.get_settings()}