from django.db import models

from tracking_fields.decorators import track


@track('name', 'age')
class Pet(models.Model):
    name = models.CharField(max_length=30)
    age = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return '{}'.format(self.name)


@track('name', 'age', 'pets', 'favourite_pet')
class Human(models.Model):
    name = models.CharField(max_length=30)
    age = models.PositiveSmallIntegerField()
    pets = models.ManyToManyField(Pet, null=True)
    favourite_pet = models.ForeignKey(
        Pet, related_name="favorited_by", null=True
    )
    height = models.PositiveIntegerField(help_text="Not tracked")

    def __unicode__(self):
        return '{}'.format(self.name)
