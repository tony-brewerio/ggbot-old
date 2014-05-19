from gbot.action import Action
from gbot import param
from gbot.models import Group

class MakeMeAdmin(Action):

    
#    expose = '!makemeadmin',

    def action(self):
        if self.player.login in ['fareko', 'YouMustSayPush', 'P.kaas', '!Rus1g'] \
            and not self.player.member_of(self.room, 'admin'):
            self.player.memberships.create(room = self.room,
                                           group = Group.get(name = 'admin'),
                                           reason = "::default::")
        else:
            self.privates.append((self.player, "fareko|YouMustSayPush only :'("))



