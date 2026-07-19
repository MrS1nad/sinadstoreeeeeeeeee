from django.urls import path
from . import views

urlpatterns = [
    path('', views.beat_list, name='beat_list'),
    path('signup/', views.signup, name='signup'),
    path('upload/', views.upload_beat, name='upload_beat'),
    path('my-beats/', views.my_beats, name='my_beats'),
    path('beat/<slug:slug>/', views.beat_detail, name='beat_detail'),
    path('beat/<slug:slug>/edit/', views.edit_beat, name='edit_beat'),
    path('beat/<slug:slug>/delete/', views.delete_beat, name='delete_beat'),
    path('beat/<slug:slug>/buy/', views.start_purchase, name='start_purchase'),
    path('beat/<slug:slug>/download/', views.download_beat, name='download_beat'),
    path('purchase/<uuid:purchase_id>/success/', views.purchase_success, name='purchase_success'),
]
