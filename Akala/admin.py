from django.contrib import admin
from .models import Category, Product, Comment, Price_history, Sold_products


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Price_history)
class PricehistoryAdmin(admin.ModelAdmin):
    list_display = ['my_price', 'my_date', 'my_product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'discounted_price', 'in_stock', 'created',
                    'updated', 'is_discount', 'quantity']
    list_filter = ['in_stock', 'is_active', 'is_discount']
    list_editable = ['price', 'discounted_price', 'in_stock', 'is_discount', 'quantity']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product_com', 'name', 'email', 'content', 'publish', 'status']
    list_filter = ['status', 'publish']
    search_fields = ['name', 'email', 'content']


@admin.register(Sold_products)
class SoldProductsAdmin(admin.ModelAdmin):
    list_display = ['price_sold', 'date_sold', 'products_sold']
