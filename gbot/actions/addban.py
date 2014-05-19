from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param

class AddBan(Action):

    expose = '+b',
    groups = 'admin', 'moder', 'censor'
    params = ['target', param.Player(),
              'reason', param.Unicode("no reason")]

    def action(self):
        if self.target.member_of(self.room, 'admin', 'moder', 'censor'):
            raise BotError('admin')

        self.ban = self.target.bans.create(room = self.room, by = self.player,
                                           reason = self.reason)
        self.announce()
        self.kick(self.target, "ban #%s" % self.ban.id)
