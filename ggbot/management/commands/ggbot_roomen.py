from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import contextlib
import socket
import sqlite3
import struct

from django.core.management.base import BaseCommand
from django.db import transaction

from ggbot.models import Room


class Command(BaseCommand):
    help = '''
    Loads list of Garena LAN rooms from _.dat file.
    You can find one in ./Room/ folder of your local Garena Plus installation.
    '''

    def add_arguments(self, parser):
        parser.add_argument('dat', type=argparse.FileType('r'),
                            help='path to Garena rooms database')

    @transaction.atomic
    def handle(self, *args, **options):
        with contextlib.closing(sqlite3.connect(options['dat'].name)) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute("""
                SELECT
                  r.RoomId,
                  r.RoomName,
                  s.IP
                FROM
                  RoomTab r
                JOIN
                  RoomServerTab s ON s.ServerId = r.ServerId
                ORDER BY
                  r.RoomId
                """)
                for room_id, room_name, room_ip in cursor.fetchall():
                    room_ip = socket.inet_ntoa(struct.pack('<I', room_ip))
                    _, created = Room.objects.update_or_create(
                        id=room_id, defaults={'name': room_name, 'ip': room_ip}
                    )
                    self.stdout.write('{:8} - {:55} - {:15} - {}\n'.format(
                        room_id, room_name.strip(), room_ip, 'created' if created else 'updated'
                    ))
