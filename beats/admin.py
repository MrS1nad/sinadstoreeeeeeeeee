from django.contrib import admin
from .models import Beat, DownloadRequest


@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'bpm', 'is_active', 'created_at')
    list_filter = ('is_active', 'genre')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(DownloadRequest)
class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = ('beat', 'name', 'telegram', 'phone', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'telegram', 'phone', 'email', 'beat__title')
