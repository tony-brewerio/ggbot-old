from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player


class Gamedetails(Action):

    expose = '.gd',
    params = ['game', param.Game(lambda action: action.player.last_game())]

    def action(self):
        if not self.game:
            raise BotError('no_game')

        self.private()


class Lastgame(Action):

    expose = '.lg',

    def action(self):
        self.game = self.room.last_game()

        self.private('gamedetails/gamedetails')




class Games(Action):

    expose = '.games',

    def action(self):
        self.games = ["#%s(%s:%s)" % (game.id, game.type, game.status)
                      for game in self.room.games.exclude(status = 'finished').\
                          order_by('-created_at')]
        self.private()