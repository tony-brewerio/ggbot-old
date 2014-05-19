from gbot.exceptions import BotError
from gbot import models

def param_required(action):
    raise BotError('param/required')

class Param(object):

    def __init__(self, default = param_required):
        self.default = default if callable(default) else lambda action: default

    def __call__(self, action, raw):
        return self.from_string(action, raw) if raw else self.default(action)

class Unicode(Param):

    def from_string(self, action, raw):
        return raw

class Player(Param):

    def from_string(self, action, raw):
        player = models.Player.by_pk(raw) or \
            models.Player.get_or(login__iexact = raw)
        if player:
            return player
        else:
            players = models.Player.filter(login__icontains = raw)[:10]
            if len(players) == 0:
                raise BotError('param/player_not_found', criteria = raw)
            elif len(players) > 1:
                raise BotError('param/player_too_many', criteria = raw, 
                               found = [p.login for p in players])
            return players[0]


class Group(Param):

    def from_string(self, action, raw):
        group = models.Group.get_or(name__iexact = raw)
        if group:
            return group
        else:
            raise BotError('param/group_not_found', criteria = raw)


class Result(Param):

    def from_string(self, action, raw):
        results = {'0': 'draw', '1': 'sentinel', '2': 'scourge'}
        if raw in results.values(): return raw
        if raw in results.keys(): return results[raw]
        raise BotError('param/wrong_result')

class Ban(Param):

    def from_string(self, action, raw):
        ban = models.Ban.get_or(pk = raw, room = getattr(action, 'room', None))
        if ban:
            return ban
        else:
            bans = Player()(action, raw).banned(getattr(action, 'room', None))
            if bans:
                return bans[0]
            raise BotError('param/ban_not_found', criteria = raw)


class Warn(Param):

    def from_string(self, action, raw):
        ban = models.Warn.get_or(pk = raw, room = getattr(action, 'room', None))
        if ban:
            return ban
        else:
            raise BotError('param/warn_not_found', criteria = raw)



class Game(Param):

    def from_string(self, action, raw):
        game = models.Game.get_or(pk = raw, room = getattr(action, 'room', None)) or \
            Player()(action, raw).last_game()
        if game:
            return game
        else:
            raise BotError('param/game_not_found', criteria = raw)






import re
from datetime import timedelta

timedelta_re = re.compile(r'(\d+)([mhd]{1})')
timedelta_kw_map = {'d': 'days', 'm': 'minutes', 'h': 'hours'}

class Timedelta(Param):
    def from_string(self, action, raw):
        return sum([timedelta(**dict([(timedelta_kw_map[t], int(n))]))
            for n, t in timedelta_re.findall(raw)], timedelta(0))


warn_types_kw_map = {
    'noob': 'noob', 'misc': 'misc violation', 'serious': 'serious violation'
}

class WarnType(Param):
    def from_string(self, action, raw):
        if raw in warn_types_kw_map: return warn_types_kw_map[raw]
        raise BotError('param/wrong_warn_type')


class Integer(Param):
    def from_string(self, action, raw):
        try:
            return int(raw)
        except ValueError:
            raise BotError('param/wrong_int', criteria = raw)










