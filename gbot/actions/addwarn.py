from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Warn
from django.db.models import F

class AddWarn(Action):

    expose = '+w',
    groups = 'admin', 'moder'
    params = ['target', param.Player(),
              'type', param.WarnType(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if 'Slaves' in self.room.name: return

        if self.type != 'noob' and not self.player.member_of(self.room, 'admin', 'moder', 'censor'):
            raise BotError('permission')

        self.warn = self.target.warns.create(room = self.room,
                by = self.player, reason = self.reason, type = self.type)


        self.target.roomstats.filter(room = self.room).update(score = F('score') - Warn.mod_score[self.type])


        self.announce()

