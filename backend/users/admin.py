from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )

    search_fields = (
        'email',
        'username'
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ['avatar']}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ['avatar']}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following'
    )
    search_fields = (
        'name',
    )
