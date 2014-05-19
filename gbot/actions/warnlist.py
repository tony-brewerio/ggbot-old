from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player


class WarnList(Action):

    expose = '.wl',
    params = ['target', param.Player(lambda action: action.player)]

    def action(self):
        self.warns = ["#%s(:%s) by %s" % (warn.id, warn.type, warn.by or "`BOT`")
                     for warn in self.target.warns.filter(room = self.room)[:10]]

        self.private()


