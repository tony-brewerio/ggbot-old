from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game
from random import randint

class Chall(Action):

    expose = '.chall',
    groups = 'leader',
    params = ['target', param.Player()]

    def action(self):
        if self.player.current_game() or self.target.current_game():
            raise BotError('already')
        if self.room.current_game():
            raise BotError('room_busy')
        if self.player == self.target:
            raise BotError('not_self')
        if not self.target.member_of(self.room, 'leader'):
            raise BotError('not_leader')

        self.game = Game.create(room = self.room, created_by = self.player,
                                accepted_by = self.target,
                                type = 'chall', status = 'chall')
        teams = ['sentinel', 'scourge']
        self.game.gamestats.create(player = self.player, captain = True,
                team = teams.pop(randint(0, 1)),
                room_score = self.room.roomstats.get(player = self.player).score)
        self.game.gamestats.create(player = self.target, captain = True,
                team = teams.pop(),
                room_score = self.room.roomstats.get(player = self.target).score)

        self.announce()


