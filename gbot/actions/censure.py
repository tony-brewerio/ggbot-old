from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from django.db.models import F
from gbot.models import Player

class Censure(Action):

    expose = []
    groups = 'player',
    params = ['target', param.Player(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if 'Slaves' in self.room.name: return

        self.game = self.player.current_game()
        if not (self.game and self.game.status == 'ongoing'):
            raise BotError('no_game')
        if self.game.warns.filter(active = True, type = 'censure',
                by = self.player, player = self.target).count():
            raise BotError('already')
        if not self.game.gamestats.filter(team__in = ['sentinel', 'scourge'],
                player = self.target).count():
            raise BotError('invalid_target')
        if self.target == self.player:
            raise BotError('self')

        self.censure = self.target.warns.create(room = self.room, game = self.game,
                by = self.player, reason = self.reason, type = 'censure')

        self.target.roomstats.filter(room = self.room).update(score = F('score') - 5)

        self.announce()


