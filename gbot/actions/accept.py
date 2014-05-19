from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game
from datetime import datetime


class Accept(Action):

    expose = '.accept',
    groups = 'leader',

    def action(self):
        game = self.room.current_game()
        if not (game and game.status == 'chall' and self.player == game.accepted_by):
            raise BotError('no_game')

        game.status = 'fresh'
        game.save()
        
        self.challed_by = game.created_by
        self.announce()




