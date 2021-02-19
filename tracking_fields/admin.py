from urllib.parse import quote

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from tracking_fields.models import TrackingEvent, TrackedFieldModification


class TrackedObjectMixinAdmin(admin.ModelAdmin):
    """
    Use this mixin to add a "Tracking" button
    next to history one on tracked object
    """
    class Meta:
        abstract = True
    change_form_template = 'tracking_fields/admin/change_form_object.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id is not None:
            extra_context['tracking_opts'] = TrackingEvent._meta
            opts = self.model._meta
            content_type = ContentType.objects.get(
                app_label=opts.app_label,
                model=opts.model_name,
            )
            extra_context['tracking_value'] = quote(u'{0}:{1}'.format(
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
        for obj in objects:
            value = u'{0}:{1}'.format(
                obj['object_content_type'], obj['object_id']
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


class TrackerEventUserFilter(admin.SimpleListFilter):
    """ Filter on users. """
    title = _("User")
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        users = qs.values('user_content_type', 'user_id',)
        lookups = {}
        for user in users:
            if user['user_content_type'] is None:
                continue
            value = u'{0}:{1}'.format(
                user['user_content_type'], user['user_id']
            )
            user_obj = (
                ContentType.objects.get_for_id(user['user_content_type'])
                .get_object_for_this_type(pk=user['user_id'])
            )
            lookups[value] = getattr(user_obj, 'username', str(user_obj))
        return [(lookup[0], lookup[1]) for lookup in lookups.items()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        value = self.value().split(':')
        return queryset.filter(
            user_content_type_id=value[0],
            user_id=value[1]
        )


class TrackedFieldModificationAdmin(admin.TabularInline):
    can_delete = False
    model = TrackedFieldModification
    readonly_fields = ('field', 'old_value', 'new_value',)

    def has_add_permission(self, request, obj=None):
        return False


class TrackingEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'action', 'object', 'object_repr')
    list_filter = ('action', TrackerEventUserFilter, TrackerEventListFilter,)
    search_fields = ('object_repr', 'user_repr',)
    readonly_fields = (
        'date', 'action', 'object', 'object_repr', 'user', 'user_repr',
    )
    inlines = (
        TrackedFieldModificationAdmin,
    )
    change_list_template = 'tracking_fields/admin/change_list_event.html'

    def changelist_view(self, request, extra_context=None):
        """ Get object currently tracked and add a button to get back to it """
        extra_context = extra_context or {}
        if 'object' in request.GET.keys():
            value = request.GET['object'].split(':')
            content_type = get_object_or_404(
                ContentType,
                id=value[0],
            )
            tracked_object = get_object_or_404(
                content_type.model_class(),
                id=value[1],
            )
            extra_context['tracked_object'] = tracked_object
            extra_context['tracked_object_opts'] = tracked_object._meta
        return super(TrackingEventAdmin, self).changelist_view(
            request, extra_context)


admin.site.register(TrackingEvent, TrackingEventAdmin)
