import json

from django.db.models import ManyToManyField

try:
    from cuser.middleware import CuserMiddleware
    CUSER = True
except ImportError:
    CUSER = False

from tracking_fields.models import (
    TrackingEvent, TrackedFieldModification,
    CREATE, UPDATE, DELETE
)


def _set_original_fields(instance):
    """
    Save fields value, only for non-m2m fields.
    """
    original_fields = {}
    for field in instance._tracked_fields:
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            original_fields[field] = getattr(instance, field)
    instance._original_fields = original_fields
    # Include pk to detect the creation of an object
    instance._original_fields['pk'] = instance.pk


def _create_event(instance, action):
    user = None
    if CUSER:
        user = CuserMiddleware.get_user()
    return TrackingEvent.objects.create(
        action=action,
        object=instance,
        object_repr=repr(instance),
        user=user,
        user_repr=repr(user),
    )


def _create_tracked_field(event, instance, field):
    return TrackedFieldModification.objects.create(
        event=event,
        field=field,
        old_value=json.dumps(instance._original_fields[field]),
        new_value=json.dumps(getattr(instance, field))
    )


def _create_create_tracking_event(instance):
    event = _create_event(instance, CREATE)
    for field in instance._tracked_fields:
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            _create_tracked_field(event, instance, field)


def _create_update_tracking_event(instance):
    event = _create_event(instance, UPDATE)
    for field in instance._tracked_fields:
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            if instance._original_fields[field] != getattr(instance, field):
                _create_tracked_field(event, instance, field)


def _create_delete_tracking_event(instance):
    _create_event(instance, DELETE)


def tracking_init(sender, instance, **kwargs):
    """
    Post init, save the current state of the object to compare it before a save
    """
    _set_original_fields(instance)


def tracking_save(sender, instance, raw, using, update_fields, **kwargs):
    """
    Post save, detect creation or changes and log them.
    We need post_save to have the object for a create.
    """
    if instance._original_fields['pk'] is None:
        # Create
        _create_create_tracking_event(instance)
    else:
        # Update
        _create_update_tracking_event(instance)
    _set_original_fields(instance)


def tracking_delete(sender, instance, using, **kwargs):
    """
    Post delete
    """
    _create_delete_tracking_event(instance)


def tracking_m2m(
        sender, instance, action, reverse, model, pk_set, using, **kwargs
):
    pass
    #import pdb; pdb.set_trace()
