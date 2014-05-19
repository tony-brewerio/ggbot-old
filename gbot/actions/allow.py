from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class Allow(Action):

    expose = '.allow',
    groups = 'host', 'leader'
    params = ['target', param.Player()]

    def action(self):
        game = self.room.fresh_game()
        if not game:
            raise BotError('nowhere_to')
        if not self.player in [game.created_by, game.accepted_by]:
            raise BotError('permission')

        game.gamestats.filter(player = self.target, team = 'forbidden').delete()

        self.announce()


