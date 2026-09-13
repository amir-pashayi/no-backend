from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from accounts.models import UserProfile

from .exports import competition_reports_zip_response, registrations_excel_response
from .models import CompetitionEvent, Festival, Pool, Registration


class GenderFilter(admin.SimpleListFilter):
    title = "Gender"
    parameter_name = "gender"

    def lookups(self, request, model_admin):
        return UserProfile.Gender.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__profile__gender=self.value())
        return queryset


class AgeGroupFilter(admin.SimpleListFilter):
    title = "Age group"
    parameter_name = "age_group"

    def lookups(self, request, model_admin):
        return (
            ("12-13", "12–13 years"),
            ("14-15", "14–15 years"),
            ("16-18", "16–18 years"),
        )

    def queryset(self, request, queryset):
        ranges = {
            "12-13": (12, 13),
            "14-15": (14, 15),
            "16-18": (16, 18),
        }
        age_range = ranges.get(self.value())
        if age_range:
            return queryset.filter(age_at_registration__range=age_range)
        return queryset


class CompetitionEventFilter(admin.SimpleListFilter):
    title = "Competition event"
    parameter_name = "competition_event"

    def lookups(self, request, model_admin):
        events = CompetitionEvent.objects.select_related("festival").order_by(
            "min_age", "order", "title"
        )
        return (
            (str(event.pk), f"{event.title} ({event.min_age}–{event.max_age})")
            for event in events
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(events__pk=self.value()).distinct()
        return queryset


@admin.register(Pool)
class PoolAdmin(ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Festival)
class FestivalAdmin(ModelAdmin):
    list_display = (
        "title",
        "registration_starts_at",
        "registration_ends_at",
        "is_active",
    )
    list_filter = ("is_active",)


@admin.register(CompetitionEvent)
class CompetitionEventAdmin(ModelAdmin):
    list_display = ("title", "festival", "min_age", "max_age", "gender", "is_active")
    list_filter = ("festival", "gender", "is_active")


@admin.register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = (
        "tracking_code",
        "user",
        "gender_display",
        "age_group_display",
        "competition_events_display",
        "pool",
        "status",
        "created_at",
    )
    list_filter = (
        GenderFilter,
        AgeGroupFilter,
        CompetitionEventFilter,
        "status",
        "festival",
        "pool",
    )
    search_fields = (
        "tracking_code",
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__profile__national_id",
    )
    readonly_fields = (
        "public_id",
        "tracking_code",
        "age_at_registration",
        "created_at",
        "updated_at",
    )
    actions = ("export_registrations_to_excel",)
    actions_list = ("export_filtered_results", "export_competition_reports_zip")
    list_select_related = ("user", "user__profile", "festival", "pool")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("events")

    @admin.display(description="Gender", ordering="user__profile__gender")
    def gender_display(self, registration):
        return registration.user.profile.get_gender_display()

    @admin.display(description="Age group", ordering="age_at_registration")
    def age_group_display(self, registration):
        age = registration.age_at_registration
        if 12 <= age <= 13:
            return "12–13 years"
        if 14 <= age <= 15:
            return "14–15 years"
        if 16 <= age <= 18:
            return "16–18 years"
        return "Outside defined groups"

    @admin.display(description="Competition events")
    def competition_events_display(self, registration):
        return ", ".join(event.title for event in registration.events.all()) or "—"

    @admin.action(description="Export selected registrations to Excel")
    def export_registrations_to_excel(self, request, queryset):
        queryset = queryset.select_related(
            "user", "user__profile", "festival", "pool"
        ).prefetch_related("events")
        return registrations_excel_response(queryset)

    @action(
        description="Export Excel",
        icon="download",
        variant=ActionVariant.PRIMARY,
        permissions=("view",),
        attrs={
            "onclick": "this.href=this.href.split('?')[0]+window.location.search"
        },
    )
    def export_filtered_results(self, request):
        changelist = self.get_changelist_instance(request)
        queryset = changelist.get_queryset(request).select_related(
            "user", "user__profile", "festival", "pool"
        ).prefetch_related("events")
        return registrations_excel_response(queryset)

    @action(
        description="Download ZIP",
        icon="folder_zip",
        variant=ActionVariant.SUCCESS,
        permissions=("view",),
    )
    def export_competition_reports_zip(self, request):
        events = CompetitionEvent.objects.order_by("order", "id")
        return competition_reports_zip_response(Registration.objects.all(), events)
