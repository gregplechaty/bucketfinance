from django.urls import path

from apps.core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/<user_id>/', views.dashboard, name='dashboard'),
    path('dashboard/buckets', views.create_bucket, name='create_bucket'),
]
