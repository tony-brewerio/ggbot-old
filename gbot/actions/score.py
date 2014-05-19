from gbot.action import Action
from gbot import param
from django.db.models import F
from gbot.exceptions import BotError

class ModScore(Action):

    expose = '!modscore',
    groups = 'admin',
    params = ['target', param.Player(),
              'amount', param.Integer()]

    def action(self):
        if self.amount > 100 or self.amount < -100:
            raise BotError('too_much')

        self.target.roomstats.filter(room = self.room).update(score = F('score') + self.amount)

        self.announce()
