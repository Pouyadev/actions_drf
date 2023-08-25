from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Recipe, Ingredient, Tag
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'last_login']
    readonly_fields = ['last_login']
    list_filter = []
    fieldsets = (
        (None, {'fields': ('email', 'last_login', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
