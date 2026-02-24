from django.db import models

class Category(models.Model):
    # فیلد parent اجازه می‌دهد هر دسته به یک دسته دیگر به عنوان "والد" وصل شود
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Category'
    )
    title = models.CharField(max_length=200, verbose_name='Category Title')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    def __str__(self):
        # این بخش کمک می‌کند در پنل ادمین متوجه شویم هر دسته زیرمجموعه چه کسی است
        if self.parent:
            return f"{self.parent.title} > {self.title}"
        return self.title

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
    name = models.CharField(max_length=200, verbose_name='Product Name')
    price = models.IntegerField(verbose_name='Price')
    description = models.TextField(verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'