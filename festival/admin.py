from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import CompetitionEvent, Festival, Pool, Registration
@admin.register(Pool)
class PoolAdmin(ModelAdmin): list_display = ("name", "is_active"); list_filter = ("is_active",); search_fields = ("name",)
@admin.register(Festival)
class FestivalAdmin(ModelAdmin): list_display = ("title", "registration_starts_at", "registration_ends_at", "is_active"); list_filter = ("is_active",)
@admin.register(CompetitionEvent)
class CompetitionEventAdmin(ModelAdmin): list_display = ("title", "festival", "min_age", "max_age", "gender", "is_active"); list_filter = ("festival", "gender", "is_active")
@admin.register(Registration)
class RegistrationAdmin(ModelAdmin): list_display = ("tracking_code", "user", "festival", "pool", "status", "created_at"); list_filter = ("status", "festival", "pool"); search_fields = ("tracking_code", "user__phone", "user__profile__national_id"); readonly_fields = ("public_id", "tracking_code", "age_at_registration", "created_at", "updated_at")
