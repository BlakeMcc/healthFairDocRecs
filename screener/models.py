import random
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.conf import settings


ROLE_CHOICES = (
    (0, 'Staff'),
    (1, 'Manager'),
    (2, 'Admin')
)

GENDER_OPTIONS = ['m', 'f', 'o']


class Organization(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=250)
    date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey('Organization')

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(User, related_name='staff')
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    organization = models.ForeignKey('Organization')

    def __str__(self):
        return str(self.user)


class Screen(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=250, db_index=True)
    params = JSONField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    event = models.ForeignKey('Event', blank=True, null=True)
    visits = models.IntegerField(default=0)

    @staticmethod
    def make_slug():
        firstword = settings.SLUG_WORDS[random.randint(0,1501)]
        num = str(random.randint(1,100))
        return ''.join([firstword,num])
