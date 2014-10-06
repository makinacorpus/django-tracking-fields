from django.test import TestCase

from tracking_fields.models import TrackingEvent, TrackedFieldModification
from tracking_fields.tests.models import Human, Pet


class TrackingEventTestCase(TestCase):
    def setUp(self):
        self.pet = Pet(name="Catz", age=12)
        self.human = Human(name="George", age=42, height=175)

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass

    def test_add(self):
        pass

    def test_remove(self):
        pass

    def test_clear(self):
        pass


class TrackedFieldModificationTestCase(TestCase):
    pass


class AdminModelTestCase(TestCase):
    pass
