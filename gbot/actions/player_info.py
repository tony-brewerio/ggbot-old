from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group, Player, Membership


class PlayerInfo(Action):

    expose = '.i',
    params = ['target', param.Player(lambda action: action.player)]

    def action(self):
        self.stats = self.target.roomstats.get(room = self.room)
        self.place = Membership.filter(active = True, room = self.room,
                                       player__roomstats__room = self.room,
                                       player__roomstats__score__gt = self.stats.score).count() + 1
        self.total = Membership.filter(active = True, room = self.room).count()

#        self.place = Player.filter(memberships__active = True,
#                                   memberships__room = self.room,
#                                   roomstats__room = self.room,
#                                   roomstats__score__gt = self.stats.score).count() + 1
#        self.total = Player.filter(memberships__active = True,
#                                   memberships__room = self.room).count()
        memberships = self.target.memberships.filter(active = True, room = self.room).\
            select_related('group')
        self.groups = ["%s(%s)" % (m.group.name, m.by or "`BOT`") for m in memberships]

        self.private()

class Top(Action):

    expose = '.top',
    
    def action(self):
        self.top = self.room.roomstats.filter(player__memberships__active = True,
                                              player__memberships__group__name = 'player',
                                              player__memberships__room = self.room).\
                                              order_by('-score').select_related('player')[:10]
        
        self.top = ["%s(%s)" % (rs.player.login, rs.score) for rs in self.top]
        self.private()


class Bot(Action):

    expose = ".bot",

    def action(self):
        self.bot = self.room.roomstats.filter(player__memberships__active = True,
                                              player__memberships__group__name = 'player',
                                              player__memberships__room = self.room).\
                                              order_by('score').select_related('player')[:10]

        self.bot = ["%s(%s)" % (rs.player.login, rs.score) for rs in self.bot]
        self.private()
