from django.urls import path

from apps.core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/buckets', views.create_bucket, name='create_bucket'),
    path('dashboard/buckets/delete/<bucket_id>/', views.delete_bucket, name='delete_bucket'),
    path('dashboard/buckets/edit/<bucket_id>/', views.edit_bucket, name='edit_bucket'),
    path('dashboard/transaction/<bucket_id>/', views.create_transaction, name='create_transaction'),
    path('dashboard/transaction/edit/<transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('dashboard/transaction/delete/<transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('dashboard/check-in/1', views.monthly_check_in_1, name='monthly_check_in_1'),
    path('dashboard/check-in/2', views.monthly_check_in_2, name='monthly_check_in_2'),
    #path('dashboard/check-in/3', views.monthly_check_in_3, name='monthly_check_in_3'),
    path('dashboard/check-in/account', views.create_account, name='create_account'),
    path('stock/', views.stock_info, name='stock_info'),
]
