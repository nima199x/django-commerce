from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product, Brand, Slider, Banner


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title', 'is_active', 'slug', 'image_preview')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    autocomplete_fields = ['parent']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;"/>',
                               obj.image.url)
        return '—'

    image_preview.short_description = 'Image'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parent')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'brand', 'price', 'is_active')
    list_display_links = ('name',)
    list_filter = ('is_active', 'category', 'brand')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_active')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;"/>',
                               obj.image.url)
        return '—'

    image_preview.short_description = 'Image'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'is_active', 'order')
    list_display_links = ('name',)
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:contain;"/>', obj.logo.url)
        return '—'

    logo_preview.short_description = 'Logo'


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'is_active', 'order')
    list_display_links = ('title',)
    list_editable = ('is_active', 'order')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" height="50" style="object-fit:cover; border-radius:4px;"/>',
                               obj.image.url)
        return '—'

    image_preview.short_description = 'Preview'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'position', 'is_active', 'order')
    list_display_links = ('title',)
    list_editable = ('is_active', 'order')
    list_filter = ('position',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" height="50" style="object-fit:cover; border-radius:4px;"/>',
                               obj.image.url)
        return '—'

    image_preview.short_description = 'Preview'
