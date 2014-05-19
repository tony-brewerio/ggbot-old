from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class Forbid(Action):

    expose = '.forbid',
    groups = 'host', 'leader'
    params = ['target', param.Player()]

    def action(self):
        game = self.room.fresh_game()
        if not game:
            raise BotError('nowhere_from')
        if self.target in [game.created_by, game.accepted_by]:
            raise BotError('host_or_cap')
        if not self.player in [game.created_by, game.accepted_by]:
            raise BotError('permission')

        if game.gamestats.filter(player = self.target).count():
            game.gamestats.filter(player = self.target).update(team = 'forbidden')
        else:
            game.gamestats.create(player = self.target, team = 'forbidden', room_score = 1000)
            
        self.announce()



