from django.contrib import admin
from .models import AIPlan, AIPlanRevision


class AIPlanRevisionInline(admin.TabularInline):
    model = AIPlanRevision
    extra = 0
    readonly_fields = ['request_text', 'provider', 'model', 'mock_mode', 'created_at']


@admin.register(AIPlan)
class AIPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'goal', 'status', 'provider', 'model', 'mock_mode', 'updated_at']
    list_filter = ['status', 'provider', 'mock_mode', 'created_at']
    search_fields = ['title', 'goal', 'source_prompt']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AIPlanRevisionInline]


@admin.register(AIPlanRevision)
class AIPlanRevisionAdmin(admin.ModelAdmin):
    list_display = ['plan', 'provider', 'model', 'mock_mode', 'created_at']
    list_filter = ['provider', 'mock_mode', 'created_at']
    search_fields = ['plan__title', 'request_text']
    readonly_fields = ['created_at']
