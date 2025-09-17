from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    path('orders/new/', views.create_order, name='create_order'),
    path('orders/terminado/', views.order_list_terminado, name='order_list_terminado'),
    path('orders/magistrales/', views.order_list_magistrales, name='order_list_magistrales'),
    path('logistics/', views.logistics_list, name='logistics_list'),
    path('logistics/export/excel/', views.export_logistics_to_excel, name='export_logistics_excel'),
]
