from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Ban
from datetime import datetime

class RemoveBan(Action):

    expose = '-b',
    groups = 'admin', 'moder', 'guard'
    params = ['ban', param.Ban(),
              'reason', param.Unicode("no reason")]


    def action(self):
        if not self.ban.active: raise BotError('already')


        if not self.ban.by or self.player.member_of(self.room, 'admin', 'moder')\
            or self.ban.by == self.player:
            Ban.filter(id = self.ban.id).update(active = False,
                                                removed_at = datetime.now(),
                                                removed_by = self.player,
                                                remove_reason = self.reason)
        else:
            raise BotError('permission')

        self.announce()

