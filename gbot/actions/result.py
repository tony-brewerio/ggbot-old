from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from django.db.models import F
from gbot.models import Player
from datetime import datetime, timedelta

class Result(Action):

    expose = '.r', '.result'
    groups = 'player',
    params = ['result', param.Result()]

    def action(self):
        self.game = self.player.current_game()
        if not (self.game and self.game.status == 'ongoing'):
            raise BotError('no_game')

        print "%s %s %s %s" % (
            datetime.now(), self.game.confirmed_at, datetime.now() - self.game.confirmed_at,
            timedelta(minutes = 10)
        )

        if (datetime.now() - self.game.confirmed_at) < timedelta(minutes = 10):
            raise BotError('10mins')

        self.game.gamestats.filter(player = self.player).update(result = self.result)

        self.private()

        votes = [(vote, self.game.teams().filter(result = vote).count())
                 for vote in ['draw', 'sentinel', 'scourge']]

        vote, num = max(votes, key = lambda x: x[1])

        if num >= self.game.teams_size() - 4:
            self.complete(vote)



    def complete(self, vote):
        self.announce('complete')

        self.old_game_status = self.game.status
        self.old_game_winner = self.game.winner

        if self.old_game_status == 'ongoing':
            self.game.finished_at = datetime.now()

        self.game.status = 'finished'
        self.game.winner = vote
        self.game.save()

        self.sentinel = list(self.game.teams().filter(team = 'sentinel').select_related('player'))
        self.scourge = list(self.game.teams().filter(team = 'scourge').select_related('player'))

        self.apply_roomstats(-1)
        self.game.teams().update(score = 0)

        if self.old_game_status == 'finished' and self.old_game_winner != 'draw':
            self.apply_wins_loses(getattr(self, self.old_game_winner), 'wins', -1)
            self.apply_wins_loses(getattr(self, 'sentinel' if self.old_game_winner == 'scourge' else 'scourge'), 'loses', -1)


        if vote in ['sentinel', 'scourge']:
            self.apply_teams()
          
        if not '!r' in self.expose:

            for gs in self.game.teams().select_related('player'):
                self.private('result/player_result', to = gs.player, score = '%+d' % gs.score)


        self.sentinel_stats = self.game.sentinel_stats()
        self.scourge_stats = self.game.scourge_stats()
        self.announce('result/results')




    def apply_teams(self):
        winners = self.sentinel if self.result == 'sentinel' else self.scourge
        losers = self.scourge if self.result == 'sentinel' else self.sentinel
        
        winners_avg = sum([gs.room_score for gs in winners]) / len(winners)
        losers_avg = sum([gs.room_score for gs in losers]) / len(losers)

        self.apply_team_score(winners, losers_avg)
        self.apply_team_score(losers, winners_avg, -1)

        if self.old_game_status == 'ongoing':
            self.apply_streaks(winners, losers)
            self.update_ips()

        self.apply_wins_loses(winners, 'wins')
        self.apply_wins_loses(losers, 'loses')

        self.apply_roomstats()
        

    def apply_wins_loses(self, team, what, direction = 1):
        for gs in team:
            self.log.debug(u"%+d %s for %s(%s)" % (direction, what, gs.player.login, gs.team))
            self.room.roomstats.filter(player = gs.player).\
                update(**dict([(what, F(what) + direction)]))


    def update_ips(self):
        for gs in self.game.teams():
            gs.ip = self.bot.ip(gs.player)    
            gs.save(force_update = True)
    
    




    def apply_roomstats(self, direction = 1):
        for gs in self.game.teams():
            gs.player.roomstats.filter(room = self.room).\
                update(score = F('score') + gs.score * direction)



    def apply_team_score(self, team, opponents_avg, multiplier = 1):
        for gs in team:
            base = 30 if multiplier > 0 else 30
            delta = gs.room_score - opponents_avg
            delta_bonus = base * (1 - 0.998 ** abs(delta))
            score = base + multiplier * (-1 if delta > 0 else 1) * delta_bonus

            self.game.gamestats.filter(pk = gs.id).\
                update(score = F('score') + score * multiplier)




    def apply_streaks(self, winners, losers):

        for l in losers:
            streak = l.player.roomstats.get(room = self.room).streak
            if streak >= 3:
                self.game.gamestats.filter(pk__in = [w.id for w in winners]).\
                    update(score = F('score') + 4 * streak)
                self.announce('result/streak', login = l.player.login, streak = streak)


        self.room.roomstats.filter(player__in = [gs.player for gs in winners], streak__lt = 0).\
            update(streak = 0)
        self.room.roomstats.filter(player__in = [gs.player for gs in winners]).\
            update(streak = F('streak') + 1)

        self.room.roomstats.filter(player__in = [gs.player for gs in losers], streak__gt = 0).\
            update(streak = 0)
        self.room.roomstats.filter(player__in = [gs.player for gs in losers]).\
            update(streak = F('streak') - 1)

