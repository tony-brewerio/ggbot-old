from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging

from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from twisted.internet import reactor
from twisted.logger import globalLogBeginner, STDLibLogObserver

from ggbot.models import League, Account
from ggbot.protocol import GarenaLeague
from ggbot.utils import rsa_create_encrypter

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''
    Runs bot's twisted daemon that handles Garena LAN connections.
    '''

    def add_arguments(self, parser):
        parser.add_argument('gkey', type=argparse.FileType('r'),
                            help='path to Garena RSA key')

    def handle(self, *args, **options):
        globalLogBeginner.beginLoggingTo([STDLibLogObserver()])
        log.info('starting up')
        try:
            rsa_encrypt = rsa_create_encrypter(options['gkey'].name)
            # find all active leagues along with all active accounts
            leagues = League.objects.filter(active=True, accounts__active=True).distinct()
            leagues = leagues.select_related('room').prefetch_related(
                Prefetch('accounts', queryset=Account.objects.filter(active=True))
            )
            for league in leagues:
                log.info(
                    'found league [%s] on room [%s] with accounts - %s',
                    league.name,
                    league.room.name,
                    ', '.join('[' + a.login + ']' for a in league.accounts.all())
                )
                GarenaLeague(league, rsa_encrypt).start()
            reactor.run()
        finally:
            log.info('all done')
