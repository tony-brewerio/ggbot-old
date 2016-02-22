from __future__ import absolute_import, division, print_function, unicode_literals

from Crypto import Random
from django.db import models

from ggbot.utils import django_decrypt, django_encrypt


class Room(models.Model):
    class Meta:
        db_table = 'ggbot_room'

    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()

    def __unicode__(self):
        return self.name


class League(models.Model):
    class Meta:
        db_table = 'ggbot_league'

    room = models.ForeignKey(Room)

    active = models.BooleanField()
    name = models.CharField(max_length=255)
    room_password = models.CharField(blank=True, max_length=10)

    def __unicode__(self):
        return self.name


class Account(models.Model):
    class Meta:
        db_table = 'ggbot_account'

    league = models.ForeignKey(League, related_name='accounts')

    active = models.BooleanField()
    login = models.CharField(max_length=255)
    password_encrypted = models.CharField(max_length=255, blank=True)
    password_encrypted_iv = models.CharField(max_length=32, blank=True)

    # I have no ida why I even bothered with this :(
    # this 'encryption' is supposed to prevent rogue admin from somehow getting password from django admin interface
    # also it helps if I accidentally print or log password somewhere

    def get_password(self):
        if self.password_encrypted:
            return django_decrypt(
                self.password_encrypted.decode('hex'), self.password_encrypted_iv.decode('hex')
            ).decode('utf-8')

    def set_password(self, password):
        if password:
            iv = Random.new().read(16)
            self.password_encrypted_iv = iv.encode('hex')
            self.password_encrypted = django_encrypt(password.encode('utf-8'), iv).encode('hex')
        else:
            self.password_encrypted_iv = ''
            self.password_encrypted = ''

    def __unicode__(self):
        return self.login
