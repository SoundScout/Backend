from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Artist, Follow, UserPreference  # ✅ Added UserPreference

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display  = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    list_filter   = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering      = ('-created_at',)

    fieldsets = (
        (None,               {'fields': ('email', 'username', 'password')}),
        ('Personal Info',    {'fields': ('profile_picture',)}),
        ('Permissions',      {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates',  {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display  = ('user', 'display_name', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('display_name', 'user__username', 'user__email')
    ordering      = ('-created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display  = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    ordering      = ('-created_at',)


# ✅ New section for UserPreference
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display  = ('user', 'favorite_genres', 'favorite_moods', 'updated_at')
    search_fields = ('user__username', 'user__email')
    ordering      = ('-updated_at',)
