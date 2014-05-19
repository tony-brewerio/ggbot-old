from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class Drop(Action):

    expose = '.drop',
    groups = 'host', 'leader'
    params = ['target', param.Player()]

    def action(self):
        game = self.room.fresh_game()
        if not game:
            raise BotError('nowhere_from')
        if self.target in [game.created_by, game.accepted_by]:
            raise BotError('host_or_cap')
        if self.target.current_game() != game:
            raise BotError('wrong_target')
        if not self.player in [game.created_by, game.accepted_by]:
            raise BotError('permission')

        game.gamestats.filter(player = self.target).delete()

        self.announce()


