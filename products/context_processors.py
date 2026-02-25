from .models import Category # 📂 چون در همان پوشه هستی از نقطه استفاده می‌کنیم

def include_categories(request):
    # 🔍 فقط دسته‌هایی که والد ندارند (سرشاخه‌ها) را می‌گیریم
    categories = Category.objects.filter(parent=None, is_active=True)
    return {
        'categories': categories # 🎁 این نام در تمام قالب‌ها در دسترس خواهد بود
    }