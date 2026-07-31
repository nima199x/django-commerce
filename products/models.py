from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Category'
    )
    title = models.CharField(max_length=200, verbose_name='Category Title')
    slug = models.SlugField(max_length=200, unique=False)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Image')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        ancestors = self.get_ancestors(include_self=True)
        return ' > '.join([node.title for node in ancestors])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                              verbose_name='Brand')
    name = models.CharField(max_length=200, verbose_name='Product Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    description = models.TextField(verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Image')
    discount = models.PositiveIntegerField(default=0, verbose_name='Discount (%)', help_text='0-100')
    is_featured = models.BooleanField(default=False, verbose_name='Featured')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock Quantity', help_text='Ignored if this product has variants below')

    def has_variants(self):
        return self.variants.exists()

    def is_in_stock(self):
        if self.has_variants():
            return self.variants.filter(stock__gt=0).exists()
        return self.stock > 0

    LOW_STOCK_THRESHOLD = 5

    def get_total_stock(self):
        if self.has_variants():
            return sum(v.stock for v in self.variants.all())
        return self.stock

    def get_min_variant_stock(self):
        """Lowest stock among variants that still have stock > 0 (ignores fully depleted variants)."""
        stocks = [v.stock for v in self.variants.all() if v.stock > 0]
        return min(stocks) if stocks else 0

    def is_low_stock(self):
        if self.has_variants():
            return any(0 < v.stock <= self.LOW_STOCK_THRESHOLD for v in self.variants.all())
        return 0 < self.stock <= self.LOW_STOCK_THRESHOLD

    def get_discounted_price(self):
        if self.discount:
            return round(self.price * (100 - self.discount) / 100, 2)
        return self.price

    def get_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def get_review_count(self):
        return self.reviews.count()

    def get_sales_count(self):
        return OrderItem.objects.filter(
            order__status='completed',
            product=self
        ).aggregate(total=models.Sum('quantity'))['total'] or 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='Product')
    size = models.CharField(max_length=50, blank=True, verbose_name='Size', help_text='e.g. S, M, L, XL, 42, 43')
    color = models.CharField(max_length=50, blank=True, verbose_name='Color', help_text='e.g. Black, Red')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock Quantity')
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Price Override', help_text='Leave blank to use the base product price'
    )
    discount_override = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Discount Override (%)',
        help_text='0-100. Leave blank to use the base product discount'
    )
    sku = models.CharField(max_length=100, blank=True, verbose_name='SKU')

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = [['product', 'size', 'color']]
        ordering = ['size', 'color']

    def __str__(self):
        parts = [p for p in [self.size, self.color] if p]
        label = ' / '.join(parts) if parts else 'Default'
        return f"{self.product.name} ({label})"

    def is_in_stock(self):
        return self.stock > 0

    def get_price(self):
        if self.price_override is not None:
            return self.price_override
        return self.product.price

    def get_discount(self):
        if self.discount_override is not None:
            return self.discount_override
        return self.product.discount

    def get_discounted_price(self):
        price = self.get_price()
        discount = self.get_discount()
        if discount:
            return round(price * (100 - discount) / 100, 2)
        return price


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name='Code')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage', verbose_name='Discount Type')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Discount Value', help_text='Percentage (0-100) or fixed amount')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Minimum Order Amount')
    categories = models.ManyToManyField(
        Category, blank=True, related_name='coupons', verbose_name='Restrict to Categories',
        help_text='Leave empty to apply to the whole site. If set, discount only applies to items from these categories.'
    )
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name='Max Uses', help_text='Leave blank for unlimited')
    times_used = models.PositiveIntegerField(default=0, verbose_name='Times Used')
    valid_from = models.DateTimeField(verbose_name='Valid From')
    valid_until = models.DateTimeField(verbose_name='Valid Until')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    def is_valid(self, order_total=None):
        from django.utils import timezone
        now = timezone.now()

        if not self.is_active:
            return False, 'This coupon is not active.'
        if now < self.valid_from:
            return False, 'This coupon is not active yet.'
        if now > self.valid_until:
            return False, 'This coupon has expired.'
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False, 'This coupon has reached its usage limit.'
        if order_total is not None and order_total < self.min_order_amount:
            return False, f'Minimum order amount for this coupon is ${self.min_order_amount}.'
        return True, ''

    def get_eligible_amount(self, cart_items):
        """
        Returns the total amount of cart items eligible for this coupon's discount.
        If no categories are set, the whole cart is eligible.
        """
        restricted_category_ids = set(self.categories.values_list('id', flat=True))
        if not restricted_category_ids:
            return sum(item.get_subtotal() for item in cart_items)

        eligible_total = 0
        for item in cart_items:
            product_category = item.product.category
            ancestor_ids = set(c.id for c in product_category.get_ancestors(include_self=True))
            if ancestor_ids & restricted_category_ids:
                eligible_total += item.get_subtotal()
        return eligible_total

    def get_discount_amount(self, eligible_amount):
        if self.discount_type == 'percentage':
            amount = eligible_amount * (self.discount_value / 100)
        else:
            amount = self.discount_value
        return min(amount, eligible_amount)


class FAQ(models.Model):
    question = models.CharField(max_length=500, verbose_name='Question')
    answer = models.TextField(verbose_name='Answer')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts', verbose_name='User')
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='Session Key')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart {self.user or self.session_key}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = [['cart', 'product', 'variant']]

    def __str__(self):
        if self.variant:
            return f"{self.quantity} x {self.product.name} ({self.variant})"
        return f"{self.quantity} x {self.product.name}"

    def get_unit_price(self):
        if self.variant:
            return self.variant.get_discounted_price()
        return self.product.get_discounted_price()

    def get_subtotal(self):
        return self.get_unit_price() * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='Customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    full_name = models.CharField(max_length=200, verbose_name='Full Name')
    address = models.CharField(max_length=300, verbose_name='Address')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Subtotal')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Coupon')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Discount Amount')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    variant = models.ForeignKey('ProductVariant', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name = models.CharField(max_length=200, verbose_name='Product Name')
    variant_label = models.CharField(max_length=100, blank=True, verbose_name='Variant')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price at Purchase')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        if self.variant_label:
            return f"{self.quantity} x {self.product_name} ({self.variant_label})"
        return f"{self.quantity} x {self.product_name}"

    def get_subtotal(self):
        return self.price * self.quantity


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Product')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='Customer')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='review', verbose_name='Purchased Item')
    rating = models.PositiveIntegerField(verbose_name='Rating (1-5)')
    comment = models.TextField(blank=True, verbose_name='Comment')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = [['user', 'order_item']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name='User')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name='Product')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = [['user', 'product']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Subscribed At')

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class Brand(models.Model):
    name = models.CharField(max_length=200, verbose_name='Brand Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    logo = models.ImageField(upload_to='brands/', null=True, blank=True, verbose_name='Logo')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Display Order')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['order', 'name']


class Slider(models.Model):
    title = models.CharField(max_length=200, verbose_name='Title', blank=True)
    image = models.ImageField(upload_to='sliders/', verbose_name='Image')
    link = models.URLField(blank=True, verbose_name='Link URL')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Display Order')

    def __str__(self):
        return self.title or f'Slide {self.pk}'

    class Meta:
        verbose_name = 'Slider'
        verbose_name_plural = 'Sliders'
        ordering = ['order']


class Banner(models.Model):
    POSITION_CHOICES = [
        ('top', 'Top Banner'),
        ('middle', 'Middle Banner'),
        ('bottom', 'Bottom Banner'),
        ('side', 'Side Banner'),
    ]
    title = models.CharField(max_length=200, verbose_name='Title', blank=True)
    image = models.ImageField(upload_to='banners/', verbose_name='Image')
    link = models.URLField(blank=True, verbose_name='Link URL')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='top', verbose_name='Position')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Display Order')

    def __str__(self):
        return self.title or f'Banner {self.pk}'

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['position', 'order']


class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='Logo')
    favicon = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='Favicon')
    site_name = models.CharField(max_length=100, default='DjangoMart', verbose_name='Site Name')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.CharField(max_length=200, blank=True, verbose_name='Address')

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    @classmethod
    def get_settings(cls):
        return cls.objects.first()