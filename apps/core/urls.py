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
]
