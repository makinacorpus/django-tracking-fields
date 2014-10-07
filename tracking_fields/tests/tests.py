from django.contrib.auth.models import User
from django.test import TestCase

from cuser.middleware import CuserMiddleware

from tracking_fields.models import (
    TrackingEvent, TrackedFieldModification,
    CREATE, UPDATE, DELETE, ADD, REMOVE, CLEAR,
)
from tracking_fields.tests.models import Human, Pet


class TrackingEventTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Toto", email="", password="secret"
        )
        self.user_repr = repr(self.user)
        CuserMiddleware.set_user(self.user)
        self.pet = Pet.objects.create(name="Catz", age=12)
        self.human = Human.objects.create(name="George", age=42, height=175)
        self.human_repr = repr(self.human)

    def test_create(self):
        """
        Test the CREATE event
        """
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 2)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, CREATE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_update(self):
        """
        Test the UPDATE event
        """
        self.human.age = 43
        self.human.save()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 3)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, UPDATE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_delete(self):
        """
        Test the DELETE event
        """
        self.human.delete()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 3)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, DELETE)
        self.assertEqual(human_event.object, None)  # Object is deleted
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_add(self):
        """
        Test the ADD event
        """
        self.human.pets.add(self.pet)
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 3)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, ADD)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_add_reverse(self):
        """
        Test the ADD event from the other side of the relationship
        """
        # Event should be the same than the one from ``test_add``
        self.pet.human_set.add(self.human)
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 3)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, ADD)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_remove(self):
        """
        Test the REMOVE event
        """
        self.human.pets.add(self.pet)
        self.human.pets.remove(self.pet)
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 4)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, REMOVE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_remove_reverse(self):
        """
        Test the REMOVE event from the other side of the relationship
        """
        # Event should be the same than the one from ``test_remove``
        self.human.pets.add(self.pet)
        self.pet.human_set.remove(self.human)
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 4)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, REMOVE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_clear(self):
        """
        Test the CLEAR event
        """
        self.human.pets.add(self.pet)
        self.human.pets.clear()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 4)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, CLEAR)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_clear_reverse(self):
        """
        Test the CLEAR event from the other side of the relationship
        """
        self.human.pets.add(self.pet)
        self.pet.human_set.clear()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 4)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        # Event is actually a removal of pet from human
        self.assertEqual(human_event.action, REMOVE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)


class TrackedFieldModificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Toto", email="", password="secret"
        )
        self.user_repr = repr(self.user)
        CuserMiddleware.set_user(self.user)
        self.pet = Pet.objects.create(name="Catz", age=12)
        self.human = Human.objects.create(name="George", age=42, height=175)
        self.human_repr = repr(self.human)

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_foreign_key(self):
        pass

    def test_add(self):
        pass

    def test_add_reverse(self):
        pass

    def test_remove(self):
        pass

    def test_remove_reverse(self):
        pass

    def test_delete(self):
        pass

    def test_delete_reverse(self):
        pass


class AdminModelTestCase(TestCase):
    pass
