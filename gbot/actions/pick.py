from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param


class Pick(Action):

    expose = '.pick',
    groups = 'leader', 'host'
    params = ['target', param.Player()]

    def action(self):
        self.game = self.room.current_game()
        if not (self.game and self.game.status == 'pick' and
            self.player in [self.game.created_by, self.game.accepted_by]):
            raise BotError('no_game')
        if self.game.picker() != self.player:
            raise BotError('no_picker')
        if not self.game.gamestats.filter(team = 'pool', player = self.target).count():
            raise BotError('wrong_target')

        self.game.gamestats.filter(team = 'pool', player = self.target).update(
            team = self.game.gamestats.get(player = self.player).team)

        self.announce()

        if self.game.teams_size() == 10:
            self.complete_picks()
        else:
            self.pool = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in
                         self.game.gamestats.filter(team = 'pool').order_by('-room_score').select_related('player')]
            self.announce('pool')



    def complete_picks(self):
        self.game.status = 'ongoing'
        self.game.save()

        sentinel = self.game.gamestats.select_related('player').\
            filter(team = 'sentinel').order_by('-room_score')
        scourge = self.game.gamestats.select_related('player').\
            filter(team = 'scourge').order_by('-room_score')

        self.sentinel = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in sentinel]
        self.scourge = ['%s(%s)' % (gs.player.login, gs.room_score) for gs in scourge]
        self.scourge_score = sum([gs.room_score for gs in scourge])
        self.sentinel_score = sum([gs.room_score for gs in sentinel])

        self.sentinel_captain = filter(lambda gs: gs.captain, sentinel)[0].player
        self.scourge_captain = filter(lambda gs: gs.captain, scourge)[0].player

        self.announce('complete')

        # we should now delete all the pool players now, to prevent ambiguity in swap
        self.game.gamestats.filter(team = 'pool').delete()