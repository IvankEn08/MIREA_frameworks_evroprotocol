from django.contrib import admin
from django.utils.html import format_html

from .models import Accident, AccidentPhoto, EmergencyMessage, Participant, Vehicle


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    autocomplete_fields = ["vehicle"]


class EmergencyMessageInline(admin.TabularInline):
    model = EmergencyMessage
    extra = 0
    fields = ["service_name", "sent_at", "status"]


class AccidentPhotoInline(admin.TabularInline):
    model = AccidentPhoto
    extra = 0
    fields = ["image", "caption", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


@admin.register(Accident)
class AccidentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "location", "occurred_at", "category", "status", "has_injured", "has_fire"
    ]
    list_filter = ["status", "has_injured", "has_fire", "occurred_at"]
    search_fields = [
        "location", "participants__full_name", "participants__vehicle__plate_number"
    ]
    date_hierarchy = "occurred_at"
    ordering = ["-occurred_at", "-id"]
    inlines = [ParticipantInline, EmergencyMessageInline, AccidentPhotoInline]
    list_select_related = False
    show_full_result_count = False

    @admin.display(description="Категория", ordering="has_injured")
    def category(self, obj):
        if obj.has_injured or obj.has_fire:
            return "Повышенная опасность"
        return "Без пострадавших"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "accident", "vehicle"]
    list_filter = ["accident__status"]
    search_fields = [
        "full_name", "phone", "vehicle__plate_number", "accident__location"
    ]
    autocomplete_fields = ["accident", "vehicle"]
    list_select_related = ["accident", "vehicle"]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "brand", "model"]
    search_fields = ["plate_number", "brand", "model"]
    ordering = ["brand", "model"]


@admin.register(EmergencyMessage)
class EmergencyMessageAdmin(admin.ModelAdmin):
    list_display = ["service_name", "accident", "sent_at", "status"]
    list_filter = ["service_name", "status", "sent_at"]
    search_fields = ["service_name", "accident__location"]
    autocomplete_fields = ["accident"]
    list_select_related = ["accident"]


@admin.register(AccidentPhoto)
class AccidentPhotoAdmin(admin.ModelAdmin):
    list_display = ["accident", "caption", "uploaded_at", "preview"]
    list_filter = ["uploaded_at"]
    search_fields = ["caption", "accident__location"]
    autocomplete_fields = ["accident"]
    readonly_fields = ["uploaded_at", "preview"]

    @admin.display(description="Предпросмотр")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="96" alt="{}">', obj.image.url, obj.caption
            )
        return "—"
