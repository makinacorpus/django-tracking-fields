from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from tracking_fields.models import TrackingEvent, TrackedFieldModification


class TrackedObjectMixinAdmin(admin.ModelAdmin):
    """
    Use this mixin to add a "Tracking" button
    next to history one on tracked object
    """
    class Meta:
        abstract = True
    change_form_template = 'tracking_fields/admin/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id is not None:
            extra_context['tracking_opts'] = TrackingEvent._meta
            opts = self.model._meta
            content_type = ContentType.objects.get(
                app_label=opts.app_label,
                model=opts.model_name,
            )
            extra_context['tracking_value'] = urlquote(u'{0}:{1}'.format(
                content_type.pk, object_id
            ))
        return super(TrackedObjectMixinAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )


class TrackerEventListFilter(admin.SimpleListFilter):
    """ Hidden filter used to get history of a particular object. """
    title = _("Object")
    parameter_name = 'object'
    template = 'tracking_fields/admin/filter.html'  # Empty template

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        objects = qs.values('object_content_type', 'object_id',)
        lookups = {}
        for object in objects:
            value = u'{0}:{1}'.format(
                object['object_content_type'], object['object_id']
            )
            lookups[value] = value
        return [(lookup[0], lookup[1]) for lookup in lookups.items()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        value = self.value().split(':')
        return queryset.filter(
            object_content_type_id=value[0],
            object_id=value[1]
        )


class TrackedFieldModificationAdmin(admin.TabularInline):
    can_delete = False
    model = TrackedFieldModification
    readonly_fields = ('field', 'old_value', 'new_value',)

    def has_add_permission(self, request):
        return False


class TrackingEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'action', 'object', 'object_repr')
    list_filter = ('action', TrackerEventListFilter,)
    search_fields = ('object_repr', 'user_repr',)
    readonly_fields = (
        'date', 'action', 'object', 'object_repr', 'user', 'user_repr',
    )
    inlines = (
        TrackedFieldModificationAdmin,
    )


admin.site.register(TrackingEvent, TrackingEventAdmin)
