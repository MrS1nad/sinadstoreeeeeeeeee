from django.urls import path
from . import views

urlpatterns = [
    path('', views.beat_list, name='beat_list'),
    path('signup/', views.signup, name='signup'),
    path('producers/', views.producer_list, name='producer_list'),
    path('producer/<str:username>/', views.producer_detail, name='producer_detail'),
    path('upload/', views.upload_beat, name='upload_beat'),
    path('my-beats/', views.my_beats, name='my_beats'),
    path('beat/<slug:slug>/', views.beat_detail, name='beat_detail'),
    path('beat/<slug:slug>/edit/', views.edit_beat, name='edit_beat'),
    path('beat/<slug:slug>/delete/', views.delete_beat, name='delete_beat'),
    path('beat/<slug:slug>/download-own/', views.download_own_beat, name='download_own_beat'),
    path('beat/<slug:slug>/leads/', views.beat_leads, name='beat_leads'),
]
