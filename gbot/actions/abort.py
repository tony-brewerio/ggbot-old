from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game
from datetime import datetime


class Abort(Action):

    expose = '.abort', '.a'
    groups = 'host', 'leader'

    def action(self):
        game = self.room.current_game()
        if not game:
            raise BotError('no_game')
        if not self.player in [game.created_by, game.accepted_by]:
            raise BotError('permission')

        game.delete()

        self.announce()


class AdmAbort(Action):

    expose = '!abort', '!a'
    groups = 'admin', 'moder', 'gm'
    params = ['game', param.Game()]

    def action(self):
        if self.game.status == 'finished':
            raise BotError('finished')

        self.game_id = self.game.id
        self.game.delete()

        self.announce()