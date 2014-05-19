from gbot.action import Action
from gbot import param
from gbot.models import Membership, Player
from gbot.exceptions import BotError

class Kick(Action):

    expose = '!k',
    groups = 'admin', 'moder', 'guard', 'censor'
    params = ['target', param.Player(),
              'reason', param.Unicode('no reason')]

    def action(self):
        if self.target.member_of(self.room, 'admin', 'moder', 'censor'):
            raise BotError('admin')

        self.kick(self.target, self.reason.encode('ascii', 'ignore')[:15])


class Kick2012(Action):
    expose = '!2012',
    groups = 'admin',
    
    def action(self):
        for id in self.bot.ip_list.keys():
            target = Player.get_or(pk = id)
            if target and Membership.filter(player = target,
                                            room = self.room,
                                            active = True).count() == 0:
                self.kick(target, "!! 2012 !!")
