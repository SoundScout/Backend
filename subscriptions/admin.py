from django.contrib import admin
from .models import Subscription, SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display  = ['name', 'max_upload_rate', 'price']
    search_fields = ['name']
    ordering      = ['name']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ['artist', 'plan', 'status', 'end_subscription', 'is_active']
    list_filter   = ['status', 'plan']
    search_fields = ['artist__user__username', 'plan__name']
    ordering      = ['-created_at']