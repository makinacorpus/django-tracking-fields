from django.db.models import ManyToManyField
from django.db.models.signals import (
    post_init, post_save, pre_delete, m2m_changed
)

from tracking_fields.tracking import (
    tracking_init, tracking_save, tracking_delete, tracking_m2m
)


def track(*fields):
    """
       Decorator used to track changes on Model's fields.

       :Example:
       >>> @track('name')
       ... class Human(models.Model):
       ...     name = models.CharField(max_length=30)
    """
    def inner(cls):
        # Small tests to ensure everything is all right
        assert not getattr(cls, '_is_tracked', False)
        for field in fields:
            # Will raise FieldDoesNotExist if there is an error
            cls._meta.get_field(field)
        # Mark the class as tracked
        cls._is_tracked = True
        cls._tracked_fields = fields
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
        # Detect m2m fields changes
        for field in fields:
            if isinstance(cls._meta.get_field(field), ManyToManyField):
                m2m_changed.connect(
                    tracking_m2m,
                    sender=getattr(cls, field).through,
                    dispatch_uid=repr(cls),
                )
        return cls
    return inner
