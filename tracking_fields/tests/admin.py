from django.contrib import admin

from tracking_fields.admin import TrackedObjectMixinAdmin
from tracking_fields.tests.models import Human


class HumanAdmin(TrackedObjectMixinAdmin):
    pass


admin.site.register(Human, HumanAdmin)
