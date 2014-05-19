from gbot.exceptions import BotError
from gbot import param
from gbot.models import Player
from gbot.actions.result import Result
from datetime import datetime

class AdmResult(Result):

    expose = '!r',
    groups = 'admin', 
    params = ['game', param.Game(),
              'result', param.Result()]

    def action(self):
        if self.game.created_at < datetime(2014, 5, 15, 16, 0):
            raise BotError('old_season')
        if not self.game.status in ['finished', 'ongoing']:
            raise BotError('wrong_game_status')

        self.complete(self.result)
