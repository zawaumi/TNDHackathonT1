from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('追加情報', {'fields': (
            'age', 'height', 'weight', 'gender', 'birth_date',
            'profile_image', 'bio'
        )}),
    )
    list_display = ['username', 'email', 'age', 'height', 'weight', 'is_active']
    search_fields = ['username', 'email']


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_at', 'device_type', 'ip_address', 'is_success']
    list_filter = ['device_type', 'is_success', 'login_at']
    search_fields = ['user__username', 'ip_address']
    date_hierarchy = 'login_at'
    readonly_fields = ['login_at']