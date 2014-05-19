from gbot.action import Action
from gbot import param

class Announce(Action):

    expose = '!ann',
    groups = 'gm', 'guard', 'voucher', 'admin', 'moder', 'censor'
    params = ['message', param.Unicode()]

    def action(self):
        self.announce()



        
