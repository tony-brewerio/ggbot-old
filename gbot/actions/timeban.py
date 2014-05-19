from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from datetime import timedelta, datetime

class TimeBan(Action):

    expose = '+tb',
    groups = 'admin', 'moder', 'censor'
    params = ['target', param.Player(),
              'timedelta', param.Timedelta(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if self.target.member_of(self.room, 'admin', 'moder', 'censor'):
            raise BotError('addban/admin')

        if self.timedelta < timedelta(minutes = 10) or \
            self.timedelta > timedelta(days = 14) or \
            (self.timedelta > timedelta(days = 3) and
                not self.player.member_of(self.room, 'admin', 'moder')):
            raise BotError('wrong_timedelta')

        self.tb = self.target.bans.create(room = self.room, by = self.player,
                                          reason = self.reason,
                                          until = self.timedelta + datetime.now())
        self.announce()
        self.kick(self.target, "ban #%s" % self.tb.id)

