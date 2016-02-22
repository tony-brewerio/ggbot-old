from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''
    Drops current ggbot tables and migrations, generates new migration and runs it
    '''

    def handle(self, *args, **options):
        self.stdout.write('removing all current migration files\n')
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'migrations')
        for fn in os.listdir(path):
            if fn != '__init__.py':
                os.remove(os.path.join(path, fn))
        self.stdout.write('dropping all application tables\n')
        drop_tables = []
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT table_name
              FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
              AND table_name LIKE 'ggbot_%'
            ''')
            drop_tables.extend(row[0] for row in cursor.fetchall())
        for drop_table in drop_tables:
            with connection.cursor() as cursor:
                cursor.execute('drop table if exists {} cascade'.format(drop_table))
        self.stdout.write('deleting all old current migrations from django migrations table\n')
        with connection.cursor() as cursor:
            cursor.execute('delete from django_migrations where app = %s', ['ggbot'])
        self.stdout.write('generating new migrations and performing migration\n')
        call_command('makemigrations', 'ggbot')
        call_command('migrate', 'ggbot')
