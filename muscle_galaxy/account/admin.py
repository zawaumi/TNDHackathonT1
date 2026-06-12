from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import User, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields = ['age']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('追加情報', {'fields': (
            'age', 'height', 'weight', 'gender', 'birth_date',
            'profile_image', 'bio'
        )}),
    )
    list_display = ['username', 'email', 'age', 'height', 'weight', 'is_active']
    search_fields = ['username', 'email']

    def age(self, obj):
        if not obj.birth_date:
            return None
        today = timezone.localdate()
        return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_at', 'device_type', 'ip_address', 'is_success']
    list_filter = ['device_type', 'is_success', 'login_at']
    search_fields = ['user__username', 'ip_address']
    date_hierarchy = 'login_at'
    readonly_fields = ['login_at']
