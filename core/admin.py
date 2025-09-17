from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product, Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # How many rows to show

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__name')
    inlines = [OrderItemInline]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nit', 'city', 'customer_type')
    list_filter = ('customer_type', 'city')
    search_fields = ('name', 'nit')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'line', 'price', 'status')
    list_filter = ('line', 'status')
    search_fields = ('code', 'name', 'composition')

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
