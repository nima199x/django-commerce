from django import template
from products.models import Category

register = template.Library()

@register.inclusion_tag('includes/category_menu.html')
def show_categories():
    # کوئری بدون فیلتر کردن والد، تا MPTT تمام درخت را ببیند
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}