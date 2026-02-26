from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title', 'is_active', 'slug')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    autocomplete_fields = ['parent']

    # این متد جادویی است که متن داخل باکس جستجو را تغییر می‌دهد
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parent')

    def display_name(self, obj):
        return str(obj) # این از همان __str__ مدل که با هم نوشتیم استفاده می‌کند
admin.site.register(Product)