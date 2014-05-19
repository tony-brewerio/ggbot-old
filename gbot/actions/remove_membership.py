from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from datetime import datetime

class RemoveMembership(Action):

    expose = '-m',
    groups = 'admin', 'moder'
    params = ['target', param.Player(),
              'group', param.Group(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if not self.target.member_of(self.room, self.group.name):
            raise BotError('not_member')

        if self.group.name in ['moder', 'admin'] and \
            not self.player.member_of(self.room, 'admin'):
            raise BotError('permission')

        self.target.memberships.filter(active = True, room = self.room, group = self.group).\
            update(active = False, removed_at = datetime.now(),
                   removed_by = self.player, remove_reason = self.reason)

        self.announce()


