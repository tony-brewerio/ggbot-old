import random

from gbot.exceptions import BotError
from gbot.action import Action
from gbot import param
from gbot.models import Game


class Password(Action):

    expose = '.pass',
    params = ['game', param.Game(lambda action: None)]

    def check_permissions(self):
        # allow to see password of any game for admins/moders
        if self.player.member_of(self.room, 'admin', 'moder'):
            return
        # allow to see password for game's players
        if self.game.teams().filter(player = self.player).count():
            return
        # deny
        raise BotError('permission')

    def generate_password(self):
        return '%030x' % random.randrange(256 ** 16)

    def action(self):
        if 'Slaves' in self.room.name: 
            return

        if self.game:
            self.check_permissions()
        else:
            self.game = self.player.last_game()

        if not self.game:
            raise BotError('no_game')

        # if there's no password on a game - make one
        if not self.game.password:
            self.game.password = self.generate_password()
            Game.objects.filter(id = self.game.id).update(password = self.game.password)

        self.private()
