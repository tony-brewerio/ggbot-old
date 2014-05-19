from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group
from datetime import datetime


class Unvouch(Action):

    expose = '-v',
    groups = 'voucher',
    params = ['target', param.Player(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if not self.target.member_of(self.room, 'player'):
            raise BotError('already')

        players = Group.get(name = 'player')

        self.target.memberships.filter(active = True, room = self.room, group = players).\
            update(active = False, removed_at = datetime.now(),
                   removed_by = self.player, remove_reason = self.reason)

        self.announce()


