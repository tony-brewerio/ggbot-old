from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class Out(Action):

    expose = '.out',
    groups = 'player',

    def action(self):
        game = self.room.fresh_game()
        if not game or game != self.player.current_game():
            raise BotError('nowhere_from')
        if self.player in [game.created_by, game.accepted_by]:
            raise BotError('host_or_cap')

        game.gamestats.filter(player = self.player).delete()

        self.announce()


