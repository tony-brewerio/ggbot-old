from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player


class BanList(Action):

    expose = '.bl',
    params = ['target', param.Player()]

    def action(self):
        self.bans = ["#%s(:%s) by %s" % (ban.id, ban.until or "permanent",
                                         ban.by.login if ban.by else "`BOT`")
                     for ban in self.target.banned(self.room)[:10]]

        self.private()


class BanInfo(Action):

    expose = '.bi',
    params = ['ban', param.Ban()]

    def action(self):

        self.private()