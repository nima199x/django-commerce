from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, FAQ , Cart, CartItem
from django.core.paginator import Paginator




def category_list(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'products/category.html', {'categories': categories})


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
        category__in=category.get_descendants(include_self=True)
    )

    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products/category.html', {
        'category': category,
        'products': products,
        'paginator': paginator,
    })

def category_menu(request, slug):
    category = get_object_or_404(Category, slug=slug)


def category(request):
    context = {}
    return render(request, 'category.html', context)

def faq_page(request):
    # گرفتن تمام سوالات از دیتابیس
    faqs = FAQ.objects.all()
    return render(request, 'products/faq.html', {'faqs': faqs})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/product_detail.html', {
        'product': product,
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
    if not request.session.session_key:
        request.session.create()
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('products:cart_detail')


def cart_detail(request):
    if not request.session.session_key:
        request.session.create()
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return render(request, 'products/cart.html', {'cart': cart})