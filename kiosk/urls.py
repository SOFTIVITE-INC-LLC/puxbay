from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:branch_id>/', views.kiosk_index, name='kiosk_index'),
]
