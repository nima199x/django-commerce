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
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        price = self.product.get_discounted_price()
        return price * self.quantity


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
    product_name = models.CharField(max_length=200, verbose_name='Product Name')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price at Purchase')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
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