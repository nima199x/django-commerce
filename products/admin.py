from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from .models import (
    Category, Product, Brand, Slider, Banner, SiteSettings,
    Order, OrderItem, Review, WishlistItem
)


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
    list_display = ('image_preview', 'name', 'category', 'brand', 'price', 'discount', 'final_price', 'is_featured', 'is_active')
    list_display_links = ('name',)
    list_filter = ('is_active', 'is_featured', 'category', 'brand')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'discount', 'is_featured', 'is_active')

    class Media:
        css = {'all': ('css/admin_compact.css',)}
        js = ('js/admin_product.js',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;"/>',
                               obj.image.url)
        return '—'
    image_preview.short_description = ''

    def final_price(self, obj):
        if obj.discount:
            return format_html(
                '<span style="color:green; font-weight:bold;">${}</span>',
                obj.get_discounted_price()
            )
        return f'${obj.price}'
    final_price.short_description = 'Final'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone', 'total', 'status', 'created_at')
    list_display_links = ('id', 'full_name')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'user__username')
    list_editable = ('status',)
    readonly_fields = ('user', 'full_name', 'address', 'phone', 'total', 'created_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_display', 'comment_preview', 'created_at')
    list_display_links = ('product',)
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('product', 'user', 'order_item', 'rating', 'comment', 'created_at')

    def rating_display(self, obj):
        return format_html('<span style="color:#f39c12;">{}</span>', '★' * obj.rating + '☆' * (5 - obj.rating))
    rating_display.short_description = 'Rating'

    def comment_preview(self, obj):
        return (obj.comment[:50] + '...') if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('user', 'product', 'created_at')


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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'email')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()