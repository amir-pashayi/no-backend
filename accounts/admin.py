from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from unfold.admin import ModelAdmin
from .models import User, UserProfile
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("phone", "first_name", "last_name", "is_active", "date_joined")
    search_fields = ("phone", "first_name", "last_name")
    ordering = ("phone",)
    fieldsets = ((None, {"fields": ("phone", "password")}), ("اطلاعات فردی", {"fields": ("first_name", "last_name", "email")}), ("دسترسی", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("phone", "first_name", "last_name", "password1", "password2", "is_staff", "is_superuser")}))
@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ("user", "national_id", "gender", "birth_date"); search_fields = ("national_id", "user__phone")
