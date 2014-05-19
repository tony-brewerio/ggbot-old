from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from gbot.models import RoomStat
from datetime import datetime
from gbot.util import split_by
from random import sample

class Confirm(Action):

    expose = '.cf',
    groups = 'leader', 'host'


    def action(self):
        self.game = self.room.current_game()
        if not (self.game and self.game.status == 'fresh' and
                self.player in [self.game.accepted_by, self.game.created_by]):
            raise BotError('no_game')
        if self.game.gamestats.exclude(team = 'forbidden').count() < 10:
            raise BotError('not_enough_pool')

        self.game.confirmed_at = datetime.now()
        getattr(self, 'confirm_' + self.game.type)()

        self.announce('confirm_' + self.game.type)

        # we should also delete all the forbidden players now, to prevent ambiguity in swap
        self.game.gamestats.filter(team = 'forbidden').delete()
    
    
    def confirm_regular(self):

        self.game.status = 'ongoing'
        
        gamestats = self.game.gamestats.filter(team = 'pool').\
            select_related('player').order_by('-room_score')
        
        sentinel, scourge = zip(*[sample(i, 2) for i in split_by(gamestats, 2)])        

        self.game.gamestats.filter(player__in = [gs.player for gs in sentinel]).\
            update(team = 'sentinel')
        self.game.gamestats.filter(player__in = [gs.player for gs in scourge]).\
            update(team = 'scourge')
        self.game.gamestats.filter(player__in = [scourge[0].player, sentinel[0].player]).\
            update(captain = True)
        
        self.game.save()

        self.sentinel = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in sentinel]
        self.scourge = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in scourge]
        self.scourge_score = sum([gs.room_score for gs in scourge])
        self.sentinel_score = sum([gs.room_score for gs in sentinel])

        
    def confirm_chall(self):
        
        self.game.status = 'pick'
        self.game.save()
        self.sentinel = self.game.gamestats.get(team = 'sentinel').player
        self.scourge = self.game.gamestats.get(team = 'scourge').player
        self.pool = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in
                     self.game.gamestats.filter(team = 'pool').order_by('-room_score').select_related('player')]
