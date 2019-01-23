from django.db import models

from tracking_fields.decorators import track


@track('vet_appointment', 'name', 'age', 'picture')
class Pet(models.Model):
    vet_appointment = models.DateTimeField(null=True)
    name = models.CharField(max_length=30)
    age = models.PositiveSmallIntegerField()
    picture = models.ImageField(upload_to=".", null=True)

    def __unicode__(self):
        return u'{0}'.format(self.name)


@track('birthday', 'name', 'age', 'pets', 'favourite_pet')
class Human(models.Model):
    birthday = models.DateField(null=True)
    name = models.CharField(max_length=30)
    age = models.PositiveSmallIntegerField()
    pets = models.ManyToManyField(Pet, null=True)
    favourite_pet = models.ForeignKey(
        Pet, related_name="favorited_by", null=True, on_delete=models.CASCADE,
    )
    height = models.PositiveIntegerField(help_text="Not tracked")

    def __unicode__(self):
        return u'{0}'.format(self.name)


@track('tenant__name', 'tenant__pets', 'tenant__favourite_pet')
class House(models.Model):
    tenant = models.OneToOneField(Human, null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'House of {0}'.format(self.tenant)
