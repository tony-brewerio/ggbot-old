from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class Sign(Action):

    expose = '.s',
    groups = 'player',

    def action(self):
        self.game = self.room.fresh_game()
        if self.player.current_game():
            raise BotError('already')
        if not self.game:
            raise BotError('nowhere_to')
        if self.game.gamestats.filter(team = 'forbidden', player = self.player).count():
            raise BotError('forbidden')
        if self.game.type != 'chall' and \
            self.game.gamestats.exclude(team = 'forbidden').count() == 10:
            raise BotError('game_is_full')

        self.game.gamestats.create(player = self.player,
                                   room_score = self.room.roomstats.get(player = self.player).score)

        self.announce()


