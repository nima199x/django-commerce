from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, Q
from .models import Category, Product, FAQ, Cart, CartItem, Order, OrderItem, Review, WishlistItem, Brand


COMPARE_SESSION_KEY = 'compare_list'
COMPARE_MAX_ITEMS = 4


def get_or_create_cart(request):
    """Returns the cart for the current user (logged in) or session (guest)."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    if not request.session.session_key:
        request.session.create()
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


def apply_sort(products, sort_key):
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-id',
        'name_asc': 'name',
        'name_desc': '-name',
    }
    return products.order_by(sort_map.get(sort_key, '-id'))


def category_list(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'products/category_list.html', {'categories': categories})


def category_products(request, parent_slug, child_slug=None):
    if child_slug:
        category = get_object_or_404(
            Category,
            slug=child_slug,
            parent__slug=parent_slug
        )
    else:
        category = get_object_or_404(Category, slug=parent_slug)

    products_list = Product.objects.filter(
        category__in=category.get_descendants(include_self=True),
        is_active=True
    )

    # Filter by brand
    brand_id = request.GET.get('brand')
    if brand_id:
        products_list = products_list.filter(brand_id=brand_id)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    # Sort
    sort_key = request.GET.get('sort', 'newest')
    products_list = apply_sort(products_list, sort_key)

    # Available brands for this category (for the filter dropdown)
    available_brands = Brand.objects.filter(
        products__category__in=category.get_descendants(include_self=True)
    ).distinct()

    paginator = Paginator(products_list, 9)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products/category.html', {
        'category': category,
        'products': products,
        'paginator': paginator,
        'available_brands': available_brands,
        'current_sort': sort_key,
        'current_brand': brand_id,
        'current_min_price': min_price,
        'current_max_price': max_price,
    })


def category_menu(request, slug):
    category = get_object_or_404(Category, slug=slug)


def category(request):
    context = {}
    return render(request, 'category.html', context)


def faq_page(request):
    faqs = FAQ.objects.all()
    return render(request, 'products/faq.html', {'faqs': faqs})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all()

    can_review = False
    if request.user.is_authenticated:
        purchased_items = OrderItem.objects.filter(
            order__user=request.user,
            order__status='completed',
            product=product
        ).exclude(review__isnull=False)
        can_review = purchased_items.exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'can_review': can_review,
    })


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ) if query else Product.objects.none()
    return render(request, 'products/search.html', {
        'products': products,
        'query': query,
    })


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('products:cart_detail')


def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    action = request.GET.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    return redirect('products:cart_detail')


def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'products/cart.html', {'cart': cart})


@login_required
def checkout(request):
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:cart_detail')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        if not full_name or not address or not phone:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'products/checkout.html', {'cart': cart})

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                address=address,
                phone=phone,
                total=cart.get_total(),
                status='completed',
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.get_discounted_price(),
                    quantity=item.quantity,
                )
            cart.items.all().delete()

        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('products:order_detail', order_id=order.id)

    return render(request, 'products/checkout.html', {'cart': cart})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'products/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'products/order_history.html', {'orders': orders})


@login_required
def submit_review(request, order_item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=order_item_id,
        order__user=request.user,
        order__status='completed'
    )

    if order_item.review.exists():
        messages.warning(request, 'You already reviewed this product.')
        return redirect('products:product_detail', slug=order_item.product.slug)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if not rating or not (1 <= int(rating) <= 5):
            messages.error(request, 'Please select a rating between 1 and 5.')
            return redirect('products:order_detail', order_id=order_item.order.id)

        Review.objects.create(
            product=order_item.product,
            user=request.user,
            order_item=order_item,
            rating=rating,
            comment=comment,
        )
        messages.success(request, 'Thank you for your review!')
        return redirect('products:product_detail', slug=order_item.product.slug)

    return redirect('products:order_detail', order_id=order_item.order.id)


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f'{product.name} added to your wish list.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def wishlist_remove(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, 'Removed from wish list.')
    return redirect('products:wishlist_detail')


@login_required
def wishlist_detail(request):
    items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'items': items})


def compare_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])

    if product.id in compare_list:
        messages.info(request, f'{product.name} is already in your compare list.')
    elif len(compare_list) >= COMPARE_MAX_ITEMS:
        messages.warning(request, f'You can compare up to {COMPARE_MAX_ITEMS} products at a time.')
    else:
        compare_list.append(product.id)
        request.session[COMPARE_SESSION_KEY] = compare_list
        messages.success(request, f'{product.name} added to compare.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def compare_remove(request, product_id):
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])
    if product_id in compare_list:
        compare_list.remove(product_id)
        request.session[COMPARE_SESSION_KEY] = compare_list
    return redirect(request.META.get('HTTP_REFERER', 'products:compare_detail'))


def compare_detail(request):
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])
    products = Product.objects.filter(id__in=compare_list)
    return render(request, 'products/compare.html', {'products': products})


def new_arrivals(request):
    products_list = Product.objects.filter(is_active=True).order_by('-id')
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'products/new_arrivals.html', {'products': products, 'paginator': paginator})


def best_sellers(request):
    products_list = Product.objects.filter(is_active=True).annotate(
        sales_count=Sum(
            'order_items__quantity',
            filter=Q(order_items__order__status='completed')
        )
    ).order_by('-sales_count')
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'products/best_sellers.html', {'products': products, 'paginator': paginator})


def specials(request):
    products_list = Product.objects.filter(is_active=True, discount__gt=0).order_by('-discount')
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'products/specials.html', {'products': products, 'paginator': paginator})