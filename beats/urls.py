from django.urls import path
from . import views

urlpatterns = [
    path('', views.beat_list, name='beat_list'),
    path('beat/<slug:slug>/', views.beat_detail, name='beat_detail'),
    path('beat/<slug:slug>/buy/', views.start_purchase, name='start_purchase'),
    path('beat/<slug:slug>/download/', views.download_beat, name='download_beat'),
    path('purchase/<uuid:purchase_id>/success/', views.purchase_success, name='purchase_success'),
]
