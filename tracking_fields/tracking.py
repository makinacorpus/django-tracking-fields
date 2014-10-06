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


# ======================= HELPERS ====================

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


def _has_changed(instance):
    """
    Check if some tracked fields have changed
    """
    for field, value in instance._original_fields.items():
        if getattr(instance, field) != value:
            return True
    return False


def _create_event(instance, action):
    """
    Create a new event, getting the use if django-cuser is available.
    """
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
    """
    Create a TrackedFieldModification for the instance.
    """
    return TrackedFieldModification.objects.create(
        event=event,
        field=field,
        old_value=json.dumps(instance._original_fields[field]),
        new_value=json.dumps(getattr(instance, field))
    )


def _create_create_tracking_event(instance):
    """
    Create a TrackingEvent and TrackedFieldModification for a CREATE event.
    """
    event = _create_event(instance, CREATE)
    for field in instance._tracked_fields:
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            _create_tracked_field(event, instance, field)


def _create_update_tracking_event(instance):
    """
    Create a TrackingEvent and TrackedFieldModification for an UPDATE event.
    """
    event = _create_event(instance, UPDATE)
    for field in instance._tracked_fields:
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            if instance._original_fields[field] != getattr(instance, field):
                _create_tracked_field(event, instance, field)


def _create_delete_tracking_event(instance):
    """
    Create a TrackingEvent for a DELETE event.
    """
    _create_event(instance, DELETE)


def _create_tracked_field_m2m(event, model, instance, sender, objects, action):
    """
    Create the ``TrackedFieldModification`` for a m2m modification.
    The first thing needed is to get the m2m field on the object being tracked.
    The current related objects are then taken (``old_value``).
    The new value is calculated in function of ``action`` (``new_value``).
    The ``TrackedFieldModification`` is created with the proper parameters.

    :param event: The TrackingEvent on which the m2m modification are made.
    :param model: The model of the object being tracked.
    :param instance: The instance of the object being tracked.
    :param sender: The m2m through relationship instance.
    :param objects: The list of objects being added/removed.
    :param action: The action from the m2m_changed signal.
    """
    for field in model._tracked_fields:
        if isinstance(instance._meta.get_field(field), ManyToManyField):
            if getattr(instance, field).through == sender:
                break
    before = list(getattr(instance, field).all())
    if action == 'pre_add':
        after = before + objects
    elif action == 'pre_remove':
        after = [obj for obj in before if obj not in objects]
    elif action == 'pre_clear':
        after = []
    before = [unicode(obj) for obj in before]
    after = [unicode(obj) for obj in after]
    return TrackedFieldModification.objects.create(
        event=event,
        field=field,
        old_value=json.dumps(before),
        new_value=json.dumps(after)
    )


# ======================= CALLBACKS ====================

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
    if not _has_changed(instance):
        return
    if instance._original_fields['pk'] is None:
        # Create
        _create_create_tracking_event(instance)
    else:
        # Update
        _create_update_tracking_event(instance)
    _set_original_fields(instance)


def tracking_delete(sender, instance, using, **kwargs):
    """
    Post delete callback
    """
    _create_delete_tracking_event(instance)


def tracking_m2m(
        sender, instance, action, reverse, model, pk_set, using, **kwargs
):
    """
    m2m_changed callback.
    The idea is to get the model and the instance of the object being tracked,
    and the different objects being added/removed. It is then send to the
    ``_create_tracked_field_m2m`` method to extract the proper attribute for
    the TrackedFieldModification.
    """
    if (action == 'post_add' or action == 'post_remove'
            or action == 'post_clear'):
        return
    action_event = {
        'pre_clear': 'CLEAR',
        'pre_add': 'ADD',
        'pre_remove': 'REMOVE',
    }
    if reverse:
        if action == 'pre_clear':
            # It will actually be a remove of ``instance`` on every
            # tracked object being related
            action = 'pre_remove'
        # Create an event for each object being tracked
        for pk in pk_set:
            tracked_instance = model.objects.get(pk=pk)
            event = _create_event(tracked_instance, action_event[action])
            objects = [instance]
            _create_tracked_field_m2m(
                event, model, tracked_instance, sender, objects, action
            )
    else:
        # Get the model of the object being tracked
        tracked_model = instance._meta.model
        event = _create_event(instance, action_event[action])
        objects = []
        if pk_set is not None:
            objects = [model.objects.get(pk=pk) for pk in pk_set]
        _create_tracked_field_m2m(
            event, tracked_model, instance, sender, objects, action
        )
