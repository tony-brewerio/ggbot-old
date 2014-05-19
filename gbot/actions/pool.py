from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player


class Pool(Action):

    expose = '.pool',
    params = ['game', param.Game(lambda action: action.player.last_game())]

    def action(self):
        if not self.game:
            raise BotError('no_game')

        self.private()


