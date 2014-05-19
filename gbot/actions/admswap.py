from gbot.actions.swap import Swap
from gbot.exceptions import BotError
from gbot import param
from django.db.models import F
from gbot.models import Player
from gbot.storage import storage


class AdmSwap(Swap):

    expose = '!swap',
    groups = 'gm', 'admin', 'moder'

    def action(self):
        if 'slaves' in self.room.name.lower():
            return

        self.game = self.target.current_game()
        self.validate()
        self.do_swap()




