from django.contrib import admin

from tracking_fields.models import TrackingEvent, TrackedFieldModification


class TrackedFieldModificationAdmin(admin.TabularInline):
    can_delete = False
    model = TrackedFieldModification
    readonly_fields = ('field', 'old_value', 'new_value',)

    def has_add_permission(self, request):
        return False


class TrackingEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'action', 'object', 'object_repr')
    list_filter = ('action',)
    readonly_fields = (
        'date', 'action', 'object', 'object_repr', 'user', 'user_repr',
    )
    inlines = (
        TrackedFieldModificationAdmin,
    )


admin.site.register(TrackingEvent, TrackingEventAdmin)
