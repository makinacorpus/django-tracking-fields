from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db.models import ManyToManyField
from django.db.models.signals import (
    post_init, post_save, pre_delete, m2m_changed
)

from tracking_fields.tracking import (
    tracking_init, tracking_save, tracking_delete, tracking_m2m
)


def _add_signals_to_cls(cls):
    # Use repr(cls) to be sure to bound the callback
    # only once for each class
    post_init.connect(
        tracking_init,
        sender=cls,
        dispatch_uid=repr(cls),
    )
    post_save.connect(
        tracking_save,
        sender=cls,
        dispatch_uid=repr(cls),
    )
    pre_delete.connect(
        tracking_delete,
        sender=cls,
        dispatch_uid=repr(cls),
    )


def _track_class_related_field(cls, field):
    """ Track a field on a related model """
    # field = field on current model
    # related_field = field on related model
    (field, related_field) = field.split('__', 1)
    field_obj = cls._meta.get_field(field)
    related_cls = field_obj.remote_field.model
    related_name = field_obj.remote_field.get_accessor_name()

    if not hasattr(related_cls, '_tracked_related_fields'):
        setattr(related_cls, '_tracked_related_fields', {})
    if related_field not in related_cls._tracked_related_fields.keys():
        related_cls._tracked_related_fields[related_field] = []

    # There can be several field from different or same model
    # related to a single model.
    # Thus _tracked_related_fields will be of the form:
    # {
    #     'field name on related model': [
    #         ('field name on current model', 'field name to current model'),
    #         ('field name on another model', 'field name to another model'),
    #         ...
    #     ],
    #     ...
    # }

    related_cls._tracked_related_fields[related_field].append(
        (field, related_name)
    )
    _add_signals_to_cls(related_cls)
    # Detect m2m fields changes
    if isinstance(related_cls._meta.get_field(related_field), ManyToManyField):
        m2m_changed.connect(
            tracking_m2m,
            sender=getattr(related_cls, related_field).through,
            dispatch_uid=repr(related_cls),
        )


def _track_class_field(cls, field):
    """ Track a field on the current model """
    if '__' in field:
        _track_class_related_field(cls, field)
        return
    # Will raise FieldDoesNotExist if there is an error
    cls._meta.get_field(field)
    # Detect m2m fields changes
    if isinstance(cls._meta.get_field(field), ManyToManyField):
        m2m_changed.connect(
            tracking_m2m,
            sender=getattr(cls, field).through,
            dispatch_uid=repr(cls),
        )


def _track_class(cls, fields):
    """ Track fields on the specified model """
    # Small tests to ensure everything is all right
    assert not getattr(cls, '_is_tracked', False)

    for field in fields:
        _track_class_field(cls, field)

    _add_signals_to_cls(cls)

    # Mark the class as tracked
    cls._is_tracked = True
    # Do not directly track related fields (tracked on related model)
    # or m2m fields (tracked by another signal)
    cls._tracked_fields = [
        field for field in fields
        if '__' not in field
    ]


def _add_get_tracking_url(cls):
    """ Add a method to get the tracking url of an object. """
    def get_tracking_url(self):
        """ return url to tracking view in admin panel """
        url = reverse('admin:tracking_fields_trackingevent_changelist')
        object_id = '{0}%3A{1}'.format(
            ContentType.objects.get_for_model(self).pk,
            self.pk
        )
        return '{0}?object={1}'.format(url, object_id)
    if not hasattr(cls, 'get_tracking_url'):
        setattr(cls, 'get_tracking_url', get_tracking_url)


def track(*fields):
    """
       Decorator used to track changes on Model's fields.

       :Example:
       >>> @track('name')
       ... class Human(models.Model):
       ...     name = models.CharField(max_length=30)
    """
    def inner(cls):
        _track_class(cls, fields)
        _add_get_tracking_url(cls)
        return cls
    return inner
