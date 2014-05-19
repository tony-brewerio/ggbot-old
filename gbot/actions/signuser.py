from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Game


class SignUser(Action):

#    expose = '.su',
    groups = 'host', 'leader'
    params = ['target', param.Player()]

    def action(self):
        game = self.room.fresh_game()
        if not self.target.member_of(self.room, 'player'):
            raise BotError('not_vouched')    
        if not game:
            raise BotError('nowhere_to')
        if self.target.current_game():
            raise BotError('already')
        if not self.player in [game.created_by, game.accepted_by]:
            raise BotError('permission')
        if game.gamestats.filter(team = 'forbidden', player = self.target).count():
            raise BotError('forbidden')
        if game.type != 'chall' and \
            game.gamestats.exclude(team = 'forbidden').count() == 10:
            raise BotError('full')

        game.gamestats.create(player = self.target,
                              room_score = self.room.roomstats.get(player = self.target).score)

        self.announce()


