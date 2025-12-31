from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.wallet_login, name='wallet_login'),
    path('dashboard/', views.wallet_dashboard, name='wallet_dashboard'),
    path('logout/', views.wallet_logout, name='wallet_logout'),
    path('manifest.json', views.manifest_json, name='wallet_manifest'),
    path('sw.js', views.service_worker_wallet, name='wallet_sw'),
]
