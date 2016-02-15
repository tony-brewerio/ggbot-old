from __future__ import absolute_import, division, print_function, unicode_literals

from Crypto.Cipher import AES
from django.conf import settings
from django.db import models


class Room(models.Model):
    class Meta:
        db_table = 'ggbot_room'

    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()

    def __unicode__(self):
        return self.name


class Account(models.Model):
    class Meta:
        db_table = 'ggbot_account'

    login = models.CharField(max_length=255)
    password_encrypted = models.TextField()

    def get_password(self):
        aes = AES.new(settings.SECRET_KEY[:32], mode=AES.MODE_CFB, IV=settings.SECRET_KEY[-16:])
        return aes.decrypt(self.password_encrypted.decode('hex')) if self.password_encrypted else None

    def set_password(self, password):
        aes = AES.new(settings.SECRET_KEY[:32], mode=AES.MODE_CFB, IV=settings.SECRET_KEY[-16:])
        self.password_encrypted = aes.encrypt(password).encode('hex') if password else None
