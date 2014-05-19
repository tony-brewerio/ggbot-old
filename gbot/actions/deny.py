from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game
from datetime import datetime


class Deny(Action):

    expose = '.deny',
    groups = 'leader',

    def action(self):
        game = self.room.current_game()
        if not (game and game.status == 'chall' and self.player == game.accepted_by):
            raise BotError('no_game')
        
        self.challed_by = game.created_by
        game.delete()

        self.announce()




