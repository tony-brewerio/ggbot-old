from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Warn
from datetime import datetime
from django.db.models import F

class RemoveWarn(Action):

    expose = '-w',
    groups = 'admin', 'moder', 'gm', 'censor'
    params = ['warn', param.Warn(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if not self.warn.active: raise BotError('already')

        if not self.warn.by or self.player.member_of(self.room, 'admin', 'moder')\
            or (self.warn.by == self.player and self.warn.type in ('noob', 'censure')):
            Warn.filter(id = self.warn.id).update(active = False,
                                                  removed_at = datetime.now(),
                                                  removed_by = self.player,
                                                  remove_reason = self.reason)


            if self.warn.at >= datetime(2014, 5, 15, 16, 0):
                self.warn.player.roomstats.filter(room = self.room).\
                    update(score = F('score') + Warn.mod_score[self.warn.type])






        else:
            raise BotError('permission')

        self.announce()

