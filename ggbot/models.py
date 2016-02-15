from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import models


class Room(models.Model):
    class Meta:
        db_table = 'ggbot_room'

    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
