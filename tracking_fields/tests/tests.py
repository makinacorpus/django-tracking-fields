# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.test import Client, TestCase
from django.utils import six, timezone
from django.utils.html import escape

from cuser.middleware import CuserMiddleware

from tracking_fields.models import (
    TrackingEvent, CREATE, UPDATE, DELETE, ADD, REMOVE, CLEAR,
)
from tracking_fields.tests.models import Human, Pet, House


class TrackingEventTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="Toto", email="", password="secret"
        )
        cls.user_repr = repr(cls.user)
        CuserMiddleware.set_user(cls.user)
        cls.pet = Pet.objects.create(name="Catz", age=12)
        cls.human = Human.objects.create(name="George", age=42, height=175)
        cls.human_repr = repr(cls.human)

    def setUp(self):
        self.user = User.objects.get()
        self.pet = Pet.objects.get()
        self.human = Human.objects.get()

    def test_create(self):
        """
        Test the CREATE event
        """
        events = TrackingEvent.objects.order_by('date').all()
        self.assertEqual(events.count(), 2)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, CREATE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_update_without_cuser(self):
        """
        Test the CREATE event without the cuser module
        """
        from tracking_fields import tracking
        tracking.CUSER = False
        self.human.age = 43
        self.human.save()
        events = TrackingEvent.objects.order_by('date').all()
        self.assertEqual(events.count(), 3)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        self.assertEqual(human_event.action, UPDATE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, None)
        self.assertEqual(human_event.user_repr, 'None')
        tracking.CUSER = True

    def test_update(self):
        """
        Test the UPDATE event
        """
        self.human.age = 43
        self.human.save()
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
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
        events = TrackingEvent.objects.order_by('date').all()
        self.assertEqual(events.count(), 4)
        human_event = events.last()
        self.assertIsNotNone(human_event.date)
        # Event is actually a removal of pet from human
        self.assertEqual(human_event.action, REMOVE)
        self.assertEqual(human_event.object, self.human)
        self.assertEqual(human_event.object_repr, self.human_repr)
        self.assertEqual(human_event.user, self.user)
        self.assertEqual(human_event.user_repr, self.user_repr)

    def test_save_with_no_change(self):
        """
        Test to save object without change, should not create an UPDATE event
        """
        self.human.save()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 2)

    def test_utf8_in_repr(self):
        """
        Test to save object with utf8 in its repr
        """
        self.human.name = u'😵'
        self.human.save()
        events = TrackingEvent.objects.all()
        self.assertEqual(events.count(), 3)


class TrackedFieldModificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Toto", email="", password="secret"
        )
        self.user_repr = repr(self.user)
        CuserMiddleware.set_user(self.user)
        self.pet = Pet.objects.create(name="Catz", age=12)
        self.pet2 = Pet.objects.create(name="Catzou", age=1)
        self.human = Human.objects.create(name="George", age=42, height=175)
        self.human.pets.add(self.pet)
        self.human_repr = repr(self.human)

    def test_create(self):
        human_event = TrackingEvent.objects.filter(action=CREATE).order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 4)
        field = human_event.fields.get(field='birthday')
        self.assertEqual(field.new_value, json.dumps(self.human.birthday))
        field = human_event.fields.get(field='name')
        self.assertEqual(field.new_value, json.dumps(self.human.name))
        field = human_event.fields.get(field='age')
        self.assertEqual(field.new_value, json.dumps(self.human.age))
        field = human_event.fields.get(field='favourite_pet')
        self.assertEqual(field.new_value, json.dumps(self.human.favourite_pet))

    def test_update(self):
        self.human.age = 43
        self.human.save()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='age')
        self.assertEqual(field.old_value, json.dumps(42))
        self.assertEqual(field.new_value, json.dumps(43))

    def test_foreign_key(self):
        self.human.favourite_pet = self.pet
        self.human.save()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='favourite_pet')
        self.assertEqual(field.old_value, json.dumps(None))
        self.assertEqual(field.new_value, json.dumps(six.text_type(self.pet)))

    def test_foreign_key_not_changed(self):
        """ Test a foreign key does not change if only other values change """
        self.human.favourite_pet = self.pet
        self.human.save()
        self.human.name = "Toto"
        self.human.save()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.first()
        self.assertEqual(field.old_value, json.dumps("George"))
        self.assertEqual(field.new_value, json.dumps("Toto"))

    def test_foreign_key_label(self):
        """ Test label of foreign keys are used in tracked fields """
        self.human.favourite_pet = self.pet
        self.human.save()
        self.human.favourite_pet = self.pet2
        self.human.save()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.first()
        self.assertEqual(field.old_value, json.dumps(six.text_type(self.pet)))
        self.assertEqual(field.new_value, json.dumps(six.text_type(self.pet2)))

    def test_add(self):
        self.human.pets.add(self.pet2)
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value,
                         json.dumps([six.text_type(self.pet)]))
        self.assertEqual(field.new_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))

    def test_add_reverse(self):
        self.pet2.human_set.add(self.human)
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value,
                         json.dumps([six.text_type(self.pet)]))
        self.assertEqual(field.new_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))

    def test_remove(self):
        self.human.pets.add(self.pet2)
        self.human.pets.remove(self.pet2)
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))
        self.assertEqual(field.new_value,
                         json.dumps([six.text_type(self.pet)]))

    def test_remove_reverse(self):
        self.human.pets.add(self.pet2)
        self.pet2.human_set.remove(self.human)
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))
        self.assertEqual(field.new_value,
                         json.dumps([six.text_type(self.pet)]))

    def test_clear(self):
        self.human.pets.add(self.pet2)
        self.human.pets.clear()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))
        self.assertEqual(field.new_value, json.dumps([]))

    def test_clear_reverse(self):
        self.human.pets.add(self.pet2)
        self.pet2.human_set.clear()
        human_event = TrackingEvent.objects.order_by('date').last()
        self.assertEqual(human_event.fields.all().count(), 1)
        field = human_event.fields.get(field='pets')
        self.assertEqual(field.old_value, json.dumps([
            six.text_type(self.pet), six.text_type(self.pet2)
        ]))
        self.assertEqual(field.new_value,
                         json.dumps([six.text_type(self.pet)]))

    def test_date(self):
        today = datetime.date.today()
        self.human.birthday = today
        self.human.save()
        human_event = TrackingEvent.objects.order_by('date').last()
        field = human_event.fields.get(field='birthday')
        self.assertEqual(field.old_value, json.dumps(None))
        self.assertEqual(field.new_value,
                         json.dumps(today.strftime('%Y-%m-%d')))

    def test_datetime(self):
        now = timezone.now()
        self.pet.vet_appointment = now
        self.pet.save()
        pet_event = TrackingEvent.objects.order_by('date').last()
        field = pet_event.fields.get(field='vet_appointment')
        self.assertEqual(field.old_value, json.dumps(None))
        self.assertEqual(field.new_value,
                         json.dumps(now.strftime('%Y-%m-%d %H:%M:%S')))

    def test_imagefield(self):
        picture = File(
            open('tracking_fields/tests/__init__.py'),
            'picture.png',
        )
        self.pet.picture = picture
        self.pet.save()
        pet_event = TrackingEvent.objects.order_by('date').last()
        field = pet_event.fields.get(field='picture')
        self.assertEqual(field.old_value, json.dumps(None))
        self.assertEqual(field.new_value, json.dumps(self.pet.picture.path))
        self.pet.picture.delete()


class TrackingRelatedTestCase(TestCase):
    def setUp(self):
        self.human = Human.objects.create(name="Toto", age=42, height=2)
        self.house = House.objects.create(tenant=self.human)
        self.content_type = ContentType.objects.get_for_model(House)

    def test_simple_change(self):
        self.human.name = "Tutu"
        self.human.save()
        house_event = TrackingEvent.objects.filter(
            object_content_type=self.content_type)
        self.assertEqual(house_event.count(), 1)
        house_event = house_event.last()
        self.assertEqual(house_event.fields.count(), 1)
        field = house_event.fields.last()
        self.assertEqual(field.old_value, '"Toto"')
        self.assertEqual(field.new_value, '"Tutu"')
        self.assertEqual(field.field, 'tenant__name')

    def test_m2m_change(self):
        pet = Pet.objects.create(name="Pet", age=4)
        self.human.pets.add(pet)
        house_event = TrackingEvent.objects.filter(
            object_content_type=self.content_type)
        self.assertEqual(house_event.count(), 1)
        house_event = house_event.last()
        self.assertEqual(house_event.fields.count(), 1)
        field = house_event.fields.last()
        self.assertEqual(field.field, 'tenant__pets')
        self.assertEqual(field.old_value, json.dumps([]))
        self.assertEqual(field.new_value, json.dumps([six.text_type(pet)]))


class AdminModelTestCase(TestCase):
    def setUp(self):
        User.objects.create_superuser('admin', '', 'password')
        self.c = Client()
        self.c.login(username="admin", password="password")
        self.human = Human.objects.create(name="George", age=42, height=175)

    def test_list(self):
        """ Test the admin view listing all objects. """
        response = self.c.get('/admin/tracking_fields/trackingevent/')
        self.assertContains(
            response,
            escape(repr(self.human)),
        )

    def test_single(self):
        """ Test the admin view listing all objects. """
        event = TrackingEvent.objects.first()
        url = '/admin/tracking_fields/trackingevent/{0}'.format(event.pk)
        response = self.c.get(url, follow=True)
        self.assertContains(
            response,
            escape(repr(self.human)),
        )
        self.assertContains(
            response,
            escape(json.dumps(self.human.name)),
        )

    def test_history_btn(self):
        """ Test the tracking button is present. """
        response = self.c.get(
            '/admin/tests/human/{}'.format(self.human.pk),
            follow=True,
        )
        self.assertContains(
            response,
            ' class="historylink">Tracking</a>',
        )

    def test_history_back_btn_is_present(self):
        """
        Test the button back to the button is present
        where there is an object filter.
        """
        content_type = ContentType.objects.get(
            app_label="tests", model="human"
        )
        param = 'object={0}%3A{1}'.format(content_type.pk, self.human.pk)
        response = self.c.get(
            '/admin/tracking_fields/trackingevent/?{0}'.format(param),
            follow=True,
        )
        self.assertContains(
            response,
            ' class="historylink">{0}</a>'.format(self.human),
        )

    def test_history_back_btn_is_not_present(self):
        """
        Test the button back to the button is not present
        where there is no object filter.
        """
        response = self.c.get(
            '/admin/tracking_fields/trackingevent/',
            follow=True,
        )
        self.assertNotContains(
            response,
            ' class="historylink">',
        )
