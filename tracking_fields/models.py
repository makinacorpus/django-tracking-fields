from __future__ import unicode_literals

import uuid

try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.db import models

# Used for object modifications
CREATE = 'CREATE'
UPDATE = 'UPDATE'
DELETE = 'DELETE'
# Used for m2m modifications
ADD = 'ADD'
REMOVE = 'REMOVE'
CLEAR = 'CLEAR'


class TrackingEvent(models.Model):
    ACTIONS = (
        (CREATE, _('Create')),
        (UPDATE, _('Update')),
        (DELETE, _('Delete')),
        (ADD, _('Add')),
        (REMOVE, pgettext_lazy('Remove from something', 'Remove')),
        (CLEAR, _('Clear')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateTimeField(
        _("Date"), auto_now_add=True, editable=False
    )

    action = models.CharField(
        _('Action'), max_length=6, choices=ACTIONS, editable=False
    )

    object_content_type = models.ForeignKey(
        ContentType,
        related_name='tracking_object_content_type',
        editable=False,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField(editable=False, null=True)
    object = GenericForeignKey('object_content_type', 'object_id')

    object_repr = models.CharField(
        _("Object representation"),
        help_text=_(
            "Object representation, useful if the object is deleted later."
        ),
        max_length=250,
        editable=False
    )

    user_content_type = models.ForeignKey(
        ContentType,
        related_name='tracking_user_content_type',
        editable=False,
        null=True,
        on_delete=models.CASCADE,
    )
    user_id = models.PositiveIntegerField(editable=False, null=True)
    user = GenericForeignKey('user_content_type', 'user_id')

    user_repr = models.CharField(
        _("User representation"),
        help_text=_(
            "User representation, useful if the user is deleted later."
        ),
        max_length=250,
        editable=False
    )

    class Meta:
        verbose_name = _('Tracking event')
        verbose_name_plural = _('Tracking events')
        ordering = ['-date']

    def get_object_model(self):
        if self.object_id is None:
            return None
        return self.object._meta.model

    def get_object_model_verbose_name(self):
        if self.object_id is None:
            return None
        return self.object._meta.verbose_name


class TrackedFieldModification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event = models.ForeignKey(
        TrackingEvent, verbose_name=_("Event"), related_name='fields',
        editable=False,
        on_delete=models.CASCADE,
    )

    field = models.CharField(_("Field"), max_length=40, editable=False)

    old_value = models.TextField(
        _("Old value"),
        help_text=_("JSON serialized"),
        null=True,
        editable=False,
    )

    new_value = models.TextField(
        _("New value"),
        help_text=_("JSON serialized"),
        null=True,
        editable=False,
    )

    class Meta:
        verbose_name = _('Tracking field modification')
        verbose_name_plural = _('Tracking field modifications')
