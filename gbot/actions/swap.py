from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from django.db.models import F
from gbot.models import Player
from gbot.storage import storage

from datetime import datetime, timedelta

class Swap(Action):

    expose = '.swap',
    groups = 'player',
    params = ['target', param.Player(),
              'swap_with', param.Player()]

    def validate(self):
        if not (self.game and self.game.status == 'ongoing'):
            raise BotError('no_game')
        if self.target.current_game() != self.game:
            raise BotError('swap/not_on_game')
        if self.swap_with.current_game():
            raise BotError('swap/playing')
        if not self.target.member_of(self.room, 'player'):
            raise BotError('signuser/not_vouched')
        if not self.player.member_of(self.room, 'admin') and (datetime.now() - self.game.confirmed_at) > timedelta(minutes = 30):
            raise BotError('swap/too_late') 

    def action(self):
        if 'slaves' in self.room.name.lower():
            return

        self.game = self.player.current_game()
        self.validate()

        key = 'game:%s:swap[%s->%s]' % (self.game.id, self.target.id, self.swap_with.id)
        self.votes = storage.get_set(key, [])

        if self.player.id in self.votes:
            raise BotError('already')
        self.votes.append(self.player.id)

        self.announce('vote')

        if len(self.votes) >= (self.game.teams_size() / 2) + 1:
            del storage[key]
            self.do_swap()


    def do_swap(self):
        old = self.game.gamestats.get(player = self.target, team__in = ['sentinel', 'scourge'])
        self.game.gamestats.create(player = self.swap_with, captain = old.captain,
                team = old.team, ip = self.bot.ip(self.swap_with),
                room_score = self.room.roomstats.get(player = self.swap_with).score)

        old.delete()
        self.announce('swap/swap')


