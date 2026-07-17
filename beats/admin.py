from django.contrib import admin
from .models import Beat, Purchase


@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'bpm', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'genre')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('beat', 'user', 'status', 'amount', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'beat__title')
