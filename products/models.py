from django.db import models
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
    # اضافه کردن فیلد برای حل خطای ادمین
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        # حالا اسلاگ و والد با هم ست می‌شوند
        unique_together = [['parent', 'slug']]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        # دریافت مسیر کامل از ریشه تا این دسته
        ancestors = self.get_ancestors(include_self=True)
        return ' > '.join([node.title for node in ancestors])


# کلاس Product بدون تغییر باقی می‌ماند
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
    name = models.CharField(max_length=200, verbose_name='Product Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    price = models.IntegerField(verbose_name='Price')
    description = models.TextField(verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Image')

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