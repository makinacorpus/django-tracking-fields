from __future__ import unicode_literals

import datetime
import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, ManyToManyField
from django.db.models.fields.files import FieldFile
from django.db.models.fields.related import ForeignKey

try:
    from xworkflows.base import StateWrapper
except ImportError:
    StateWrapper = type('StateWrapper', (object,), dict())

try:
    from cuser.middleware import CuserMiddleware
    CUSER = True
except ImportError:
    CUSER = False

from tracking_fields.models import (
    TrackingEvent, TrackedFieldModification,
    CREATE, UPDATE, DELETE
)

logger = logging.getLogger(__name__)


# ======================= HELPERS ====================

def _set_original_fields(instance):
    """
    Save fields value, only for non-m2m fields.
    """
    original_fields = {}

    def _set_original_field(instance, field):
        if instance.pk is None:
            original_fields[field] = None
        else:
            if isinstance(instance._meta.get_field(field), ForeignKey):
                # Only get the PK, we don't want to get the object
                # (which would make an additional request)
                original_fields[field] = getattr(instance,
                                                 '{0}_id'.format(field))
            else:
                # Do not store deferred fields
                if field in instance.__dict__:
                    original_fields[field] = getattr(instance, field)

    for field in getattr(instance, '_tracked_fields', []):
        _set_original_field(instance, field)
    for field in getattr(instance, '_tracked_related_fields', {}).keys():
        _set_original_field(instance, field)

    instance._original_fields = original_fields
    # Include pk to detect the creation of an object
    instance._original_fields['pk'] = instance.pk


def _has_changed(instance):
    """
    Check if some tracked fields have changed
    """
    for field, value in instance._original_fields.items():
        if field != 'pk' and \
           not isinstance(instance._meta.get_field(field), ManyToManyField):
            try:
                if field in getattr(instance, '_tracked_fields', []):
                    if isinstance(instance._meta.get_field(field), ForeignKey):
                        if getattr(instance, '{0}_id'.format(field)) != value:
                            return True
                    else:
                        if getattr(instance, field) != value:
                            return True
            except TypeError:
                # Can't compare old and new value, should be different.
                return True
    return False


def _has_changed_related(instance):
    """
    Check if some related tracked fields have changed
    """
    tracked_related_fields = getattr(
        instance,
        '_tracked_related_fields',
        {}
    ).keys()
    for field, value in instance._original_fields.items():
        if field != 'pk' and \
           not isinstance(instance._meta.get_field(field), ManyToManyField):
            if field in tracked_related_fields:
                if isinstance(instance._meta.get_field(field), ForeignKey):
                    if getattr(instance, '{0}_id'.format(field)) != value:
                        return True
                else:
                    if getattr(instance, field) != value:
                        return True
    return False


def _create_event(instance, action):
    """
    Create a new event, getting the use if django-cuser is available.
    """
    user = None
    user_repr = repr(user)
    if CUSER:
        user = CuserMiddleware.get_user()
        user_repr = repr(user)
        if user is not None and user.is_anonymous:
            user = None
    return TrackingEvent.objects.create(
        action=action,
        object=instance,
        object_repr=repr(instance),
        user=user,
        user_repr=user_repr,
    )


def _serialize_field(field):
    if isinstance(field, datetime.datetime):
        return json.dumps(
            field.strftime('%Y-%m-%d %H:%M:%S'), ensure_ascii=False
        )
    if isinstance(field, datetime.date):
        return json.dumps(
            field.strftime('%Y-%m-%d'), ensure_ascii=False
        )
    if isinstance(field, FieldFile):
        try:
            return json.dumps(field.path, ensure_ascii=False)
        except ValueError:
            # No file
            return json.dumps(None, ensure_ascii=False)
    if isinstance(field, Model):
        return json.dumps(str(field),
                          ensure_ascii=False)
    if isinstance(field, StateWrapper):
        return json.dumps(field.name,
                          ensure_ascii=False)
    try:
        return json.dumps(field, ensure_ascii=False)
    except TypeError:
        logger.warning("Could not serialize field {0}".format(repr(field)))
        return json.dumps(repr(field), ensure_ascii=False)


def _create_tracked_field(event, instance, field, fieldname=None):
    """
    Create a TrackedFieldModification for the instance.

    :param event: The TrackingEvent on which to add TrackingField
    :param instance: The instance on which the field is
    :param field: The field name to track
    :param fieldname: The displayed name for the field. Default to field.
    """
    fieldname = fieldname or field
    if isinstance(instance._meta.get_field(field), ForeignKey):
        # We only have the pk, we need to get the actual object
        model = instance._meta.get_field(field).remote_field.model
        pk = instance._original_fields[field]
        try:
            old_value = model.objects.get(pk=pk)
        except model.DoesNotExist:
            old_value = None
    else:
        old_value = instance._original_fields[field]
    return TrackedFieldModification.objects.create(
        event=event,
        field=fieldname,
        old_value=_serialize_field(old_value),
        new_value=_serialize_field(getattr(instance, field))
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
            try:
                if isinstance(instance._meta.get_field(field), ForeignKey):
                    # Compare pk
                    value = getattr(instance, '{0}_id'.format(field))
                else:
                    value = getattr(instance, field)
                if instance._original_fields[field] != value:
                    _create_tracked_field(event, instance, field)
            except TypeError:
                # Can't compare old and new value, should be different.
                _create_tracked_field(event, instance, field)


def _create_update_tracking_related_event(instance):
    """
    Create a TrackingEvent and TrackedFieldModification for an UPDATE event
    for each related model.
    """
    events = {}
    # Create a dict mapping related model field to modified fields
    for field, related_fields in instance._tracked_related_fields.items():
        if not isinstance(instance._meta.get_field(field), ManyToManyField):
            if isinstance(instance._meta.get_field(field), ForeignKey):
                # Compare pk
                value = getattr(instance, '{0}_id'.format(field))
            else:
                value = getattr(instance, field)
            if instance._original_fields[field] != value:
                for related_field in related_fields:
                    events.setdefault(related_field, []).append(field)

    # Create the events from the events dict
    for related_field, fields in events.items():
        try:
            related_instances = getattr(instance, related_field[1])
        except ObjectDoesNotExist:
            continue

        # FIXME: isinstance(related_instances, RelatedManager ?)
        if hasattr(related_instances, 'all'):
            related_instances = related_instances.all()
        else:
            related_instances = [related_instances]
        for related_instance in related_instances:
            event = _create_event(related_instance, UPDATE)
            for field in fields:
                fieldname = '{0}__{1}'.format(related_field[0], field)
                _create_tracked_field(
                    event, instance, field, fieldname=fieldname
                )


def _create_delete_tracking_event(instance):
    """
    Create a TrackingEvent for a DELETE event.
    """
    _create_event(instance, DELETE)


def _get_m2m_field(model, sender):
    """
    Get the field name from a model and a sender from m2m_changed signal.
    """
    for field in getattr(model, '_tracked_fields', []):
        if isinstance(model._meta.get_field(field), ManyToManyField):
            if getattr(model, field).through == sender:
                return field
    for field in getattr(model, '_tracked_related_fields', {}).keys():
        if isinstance(model._meta.get_field(field), ManyToManyField):
            if getattr(model, field).through == sender:
                return field


def _create_tracked_field_m2m(event, instance, field, objects, action,
                              fieldname=None):
    fieldname = fieldname or field
    before = list(getattr(instance, field).all())
    if action == 'ADD':
        after = before + objects
    elif action == 'REMOVE':
        after = [obj for obj in before if obj not in objects]
    elif action == 'CLEAR':
        after = []
    before = list(map(str, before))
    after = list(map(str, after))
    return TrackedFieldModification.objects.create(
        event=event,
        field=fieldname,
        old_value=json.dumps(before),
        new_value=json.dumps(after)
    )


def _create_tracked_event_m2m(model, instance, sender, objects, action):
    """
    Create the ``TrackedEvent`` and it's related ``TrackedFieldModification``
    for a m2m modification.
    The first thing needed is to get the m2m field on the object being tracked.
    The current related objects are then taken (``old_value``).
    The new value is calculated in function of ``action`` (``new_value``).
    The ``TrackedFieldModification`` is created with the proper parameters.

    :param model: The model of the object being tracked.
    :param instance: The instance of the object being tracked.
    :param sender: The m2m through relationship instance.
    :param objects: The list of objects being added/removed.
    :param action: The action from the m2m_changed signal.
    """
    field = _get_m2m_field(model, sender)
    if field in getattr(model, '_tracked_related_fields', {}).keys():
        # In case of a m2m tracked on a related model
        related_fields = model._tracked_related_fields[field]
        for related_field in related_fields:
            try:
                related_instances = getattr(instance, related_field[1])
            except ObjectDoesNotExist:
                continue
            # FIXME: isinstance(related_instances, RelatedManager ?)
            if hasattr(related_instances, 'all'):
                related_instances = related_instances.all()
            else:
                related_instances = [related_instances]
            for related_instance in related_instances:
                event = _create_event(related_instance, action)
                fieldname = '{0}__{1}'.format(related_field[0], field)
                _create_tracked_field_m2m(
                    event, instance, field, objects, action, fieldname
                )
    if field in getattr(model, '_tracked_fields', []):
        event = _create_event(instance, action)
        _create_tracked_field_m2m(event, instance, field, objects, action)


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
    if _has_changed(instance):
        if instance._original_fields['pk'] is None:
            # Create
            _create_create_tracking_event(instance)
        else:
            # Update
            _create_update_tracking_event(instance)
    if _has_changed_related(instance):
        # Because an object need to be saved before being related,
        # it can only be an update
        _create_update_tracking_related_event(instance)
    if _has_changed(instance) or _has_changed_related(instance):
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
    action_event = {
        'pre_clear': 'CLEAR',
        'pre_add': 'ADD',
        'pre_remove': 'REMOVE',
    }
    if (action not in action_event.keys()):
        return
    if reverse:
        if action == 'pre_clear':
            # It will actually be a remove of ``instance`` on every
            # tracked object being related
            action = 'pre_remove'
            # pk_set is None for clear events, we need to get objects' pk.
            field = _get_m2m_field(model, sender)
            field = model._meta.get_field(field).remote_field.get_accessor_name()
            pk_set = set([obj.id for obj in getattr(instance, field).all()])
        # Create an event for each object being tracked
        for pk in pk_set:
            tracked_instance = model.objects.get(pk=pk)
            objects = [instance]
            _create_tracked_event_m2m(
                model, tracked_instance, sender, objects, action_event[action]
            )
    else:
        # Get the model of the object being tracked
        tracked_model = instance._meta.model
        objects = []
        if pk_set is not None:
            objects = [model.objects.get(pk=pk) for pk in pk_set]
        _create_tracked_event_m2m(
            tracked_model, instance, sender, objects, action_event[action]
        )
