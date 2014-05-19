from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player


class VouchesLeft(Action):

    expose = '?v',
    params = ['target', param.Player(lambda action: action.player)]

    def action(self):
        self.vouches = self.target.vouches_left(self.room)

        self.private()

