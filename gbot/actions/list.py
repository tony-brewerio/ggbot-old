from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player, RoomStat


class List(Action):

    expose = '.list',
    params = ['group', param.Group()]

    def action(self):
        self.logins = [p.login for p in Player.filter(memberships__active = True,
                                                      memberships__room = self.room,
                                                      memberships__group = self.group)[:10]]

        self.private()


class ListStreaks(Action):

    expose = '.ls',

    def action(self):
        roomstats = RoomStat.filter(room = self.room, streak__gte = 5)\
                                 .select_related('player').order_by('-streak')[:20]
        self.streaks = ', '.join("%s(+%s)" % (rs.player.login, rs.streak) for rs in roomstats)

        self.private()
