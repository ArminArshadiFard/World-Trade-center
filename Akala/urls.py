from django.urls import path
from . import views
from .views import line_chart_json

app_name = 'Akala'

urlpatterns = [
    path('', views.product_all, name='product_all'),
    path('<slug:slug>', views.product_detail, name='product_detail'),
    path('store/<slug:category_slug>/', views.category_list, name='category_list'),

    path('login/', views.login_view, name='login_user'),
    path('seller_signup/', views.seller_signup, name='seller_signup'),
    path('logoutseller/', views.logoutSeller, name='logout_seller'),

    path('edit_product/<slug:slug>/', views.edit_product, name='edit_product'),
    path('delete_product/<slug:slug>/', views.delete_product, name='delete_product'),
    path('user_page/', views.user_page, name='user_page'),

    path('basket_show/', views.basket_show, name='basket_show'),
    path('delete_basket_product/<slug:slug>/', views.delete_basket_product, name='delete_basket_product'),
    path('basket_delete_all/', views.basket_delete_all, name='basket_delete_all'),
    path('buy_basket/', views.buy_basket, name='buy_basket'),

    # path('chart/', line_chart, name='line_chart'),
    path('chartJSON/<slug:slug>', line_chart_json, name='line_chart_json'),

    # path('test/', views.LineChartJSONView.as_view, name='test')
]
