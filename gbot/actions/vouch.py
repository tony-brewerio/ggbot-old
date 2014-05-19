from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import Group

class Vouch(Action):

    expose = '+v',
    groups = 'voucher',
    params = ['target', param.Player(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if self.target.member_of(self.room, 'player'):
            raise BotError('already')

#        if self.bot.name == "SlaVe":
#            raise BotError('addmembership/no_player')
        
        if self.player.vouches_left(self.room) <= 0:
            raise BotError('addmembership/limit')

        self.vouch = self.target.memberships.create(reason = self.reason,
                                                    room = self.room,
                                                    group = Group.get(name = 'player'),
                                                    by = self.player)
        self.announce()


