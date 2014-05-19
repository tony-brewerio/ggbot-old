from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class StartGame(Action):

    expose = '.sg',
    groups = 'host', 'leader'
    params = ['mode', param.Unicode('-cm')]

    def action(self):
        if self.player.current_game():
            raise BotError('already')
        if self.room.current_game():
            raise BotError('room_busy')

        self.game = Game.create(room = self.room, created_by = self.player, mode = self.mode)
        self.game.gamestats.create(player = self.player,
                                   room_score = self.room.roomstats.get(player = self.player).score)
            
        self.announce()


