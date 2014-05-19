from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param

class AddMembership(Action):

    expose = '+m',
    groups = 'admin', 'moder'
    params = ['target', param.Player(),
              'group', param.Group(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if self.target.member_of(self.room, self.group.name):
            raise BotError('already')

#        if not self.player.member_of(self.room, 'admin') and self.bot.name == "SlaVe" and self.group.name == "player":
#            raise BotError('no_player')

        if self.group.name in ['moder', 'admin'] and \
            not self.player.member_of(self.room, 'admin'):
            raise BotError('permission')

        if self.player.vouches_left(self.room) <= 0:
            raise BotError('addmembership/limit')

        self.membership = self.target.memberships.create(reason = self.reason,
                                                         room = self.room,
                                                         group = self.group,
                                                         by = self.player)
        self.announce()


