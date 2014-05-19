from django.db import models
from django.db.models import Q, Sum
from datetime import datetime

class Model(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get(cls, *args, **kwargs): return cls.objects.get(*args, **kwargs)

    @classmethod
    def filter(cls, *args, **kwargs): return cls.objects.filter(*args, **kwargs)

    @classmethod
    def exclude(cls, *args, **kwargs): return cls.objects.exclude(*args, **kwargs)

    @classmethod
    def create(cls, **kwargs): return cls.objects.create(**kwargs)

    @classmethod
    def raw(cls, *args, **kwargs): return cls.objects.raw(*args, **kwargs)

    @classmethod
    def get_or_create(cls, *args, **kwargs): return cls.objects.get_or_create(*args, **kwargs)

    @classmethod
    def by_pk(cls, pk):
        try:
            return cls.get_or(pk = pk)
        except ValueError:
            return None

    @classmethod
    def get_or(cls, *args, **kwargs):
        try:
            return cls.get(**kwargs)
        except (cls.DoesNotExist, cls.MultipleObjectsReturned, ValueError):
            return args[0] if args else None


class Account(Model):
    class Meta:
        db_table = 'accounts'

    login = models.TextField()
    packet = models.TextField()
    port = models.IntegerField()


class Group(Model):
    class Meta:
        db_table = 'groups'

    name = models.TextField()


class Room(Model):
    class Meta:
        db_table = 'rooms'

    name = models.TextField()
    ip = models.IPAddressField()

    def current_game(self):
        game = self.games.filter(status__in = ['chall', 'fresh', 'pick'])
        if game:
            return game[0]

    def fresh_game(self):
        game = self.games.filter(status = 'fresh')
        if game:
            return game[0]

    def last_game(self):
        return self.games.latest('created_at')

    def __unicode__(self):
        return self.name

class Player(Model):
    class Meta:
        db_table = 'players'

    login = models.TextField(default = '::placeholder::')

    def __unicode__(self):
        return self.login

    def last_game(self):
        try:
            return self.games().latest('created_at')
        except Game.DoesNotExist:
            pass

    def member_of(self, room, *groups):
        return self.memberships.filter(active = True,
                                       room = room,
                                       group__name__in = groups).count()

    def vouches_left(self, room):
        if self.member_of(room, 'admin'): return 100500
        if self.member_of(room, 'moder', 'voucher'):
            return 60 - self.memberships_by.filter(room = room, active = True, at__gte = datetime(2014, 5, 15, 16, 0)).count()
        return 0

    def games(self):
        return Game.exclude(gamestats__team = 'forbidden').\
                    filter(gamestats__player = self, gamestats__truanted = False)

    def current_game(self):
        game = list(Game.raw("""
            select g.*
            from games g, gamestats gs
            where
                gs.game_id = g.id and gs.player_id = %s
                and g.status <> 'finished'
                and gs.team <> 'forbidden'
                and gs.truanted = false
                and not (g.status = 'ongoing' and gs.team = 'pool')
            order by g.created_at desc
            limit 1
        """, [self.id]))

#        game = self.games().exclude(status = 'finished').\
#            exclude(status = 'ongoing', gamestats__team = 'pool')[:1]
        if game:
            return game[0]

    def banned(self, room):
        return self.bans.filter(Q(until__gte = datetime.now()) | Q(until = None),
                                active = True, room = room).order_by('-at')


class Game(Model):
    class Meta:
        db_table = 'games'

    type = models.TextField(blank = False, default = 'regular')
    status = models.TextField(blank = False, default = 'fresh')
    winner = models.TextField(blank = False, default = 'draw')
    mode = models.TextField(blank = False, default = '-cm')

    created_at = models.DateTimeField(auto_now_add = True)
    confirmed_at = models.DateTimeField()
    finished_at = models.DateTimeField()

    room = models.ForeignKey(Room, related_name = 'games')
    created_by = models.ForeignKey(Player, related_name = 'games_created', null = True)
    accepted_by = models.ForeignKey(Player, related_name = 'games_accepted', null = True)

    password = models.TextField(null = True)

    def teams(self):
        return self.gamestats.filter(truanted = False, team__in = ['sentinel', 'scourge'])
    def team(self, team):
        return self.gamestats.filter(team = team, truanted = False).order_by('-captain').select_related('player')

    def sentinel(self): return self.team('sentinel')
    def scourge(self): return self.team('scourge')

    def team_score(self, team):
        return sum([gs.room_score for gs in self.team(team)])
    def sentinel_score(self): return self.team_score('sentinel')
    def scourge_score(self): return self.team_score('scourge')

    def team_stats(self, team):
        return ", ".join(["%s(%s%s)" % (gs.player.login,
            ("%+d" % gs.score) if self.status == 'finished' else gs.room_score,
            '') for gs in self.team(team)])

    def sentinel_stats(self): return self.team_stats('sentinel')
    def scourge_stats(self): return self.team_stats('scourge')
    def pool_stats(self): return self.team_stats('pool')


    def teams_size(self):
        return self.teams().count()

    def picker(self):
        sentinel_captain = self.gamestats.select_related('player').\
            get(team = 'sentinel', captain = True).player
        scourge_captain = self.gamestats.select_related('player').\
            get(team = 'scourge', captain = True).player

        ts = self.teams_size()
        if ts == 2:
            return sentinel_captain
        elif ts <= 4:
            return scourge_captain
        elif ts <= 6:
            return sentinel_captain
        elif ts <= 8:
            return scourge_captain
        else:
            return sentinel_captain
 



class Ban(Model):
    class Meta:
        db_table = 'bans'

    active = models.BooleanField(default = True)

    room = models.ForeignKey(Room, related_name = 'bans')
    player = models.ForeignKey(Player, related_name = 'bans')

    at = models.DateTimeField(auto_now_add = True)
    until = models.DateTimeField()
    by = models.ForeignKey(Player, related_name = 'bans_by')
    reason = models.TextField()

    removed_at = models.DateTimeField()
    removed_by = models.ForeignKey(Player, related_name = 'bans_removed')
    remove_reason = models.TextField()



class Warn(Model):
    class Meta:
        db_table = 'warns'

    mod_score = {
        'truant': 100,
        'serious violation': 80,
        'misc violation': 60,
        'noob': 40,
        'censure': 5
    }

    active = models.BooleanField(default = True)
    type = models.TextField(null = False, blank = False)

    room = models.ForeignKey(Room, related_name = 'warns')
    player = models.ForeignKey(Player, related_name = 'warns')
    game = models.ForeignKey(Game, related_name = 'warns')

    at = models.DateTimeField(auto_now_add = True)
    by = models.ForeignKey(Player, null = True, related_name = 'warns_by')
    reason = models.TextField()

    removed_at = models.DateTimeField()
    removed_by = models.ForeignKey(Player, related_name = 'warns_removed')
    remove_reason = models.TextField()



class GameStat(Model):
    class Meta:
        db_table = 'gamestats'

    team = models.TextField(blank = False, default = 'pool')
    result = models.TextField(null = True, default = None)
    score = models.IntegerField(default = 0)
    room_score = models.IntegerField()
    ip = models.IPAddressField(null = True)

    captain = models.BooleanField(default = False)
    truanted = models.BooleanField(default = False)

    player = models.ForeignKey(Player, related_name = 'gamestats')
    game = models.ForeignKey(Game, related_name = 'gamestats')


class RoomStat(Model):
    class Meta:
        db_table = 'roomstats'

    score = models.IntegerField(default = 1000)
    streak = models.IntegerField(default = 0)
    wins = models.IntegerField(default = 0)
    loses = models.IntegerField(default = 0)

    player = models.ForeignKey(Player, related_name = 'roomstats')
    room = models.ForeignKey(Room, related_name = 'roomstats')


class Membership(Model):
    class Meta:
        db_table = 'memberships'

    active = models.BooleanField(default = True)

    room = models.ForeignKey(Room, related_name = 'memberships')
    player = models.ForeignKey(Player, related_name = 'memberships')
    group = models.ForeignKey(Group, related_name = 'memberships')

    at = models.DateTimeField(auto_now_add = True)
    by = models.ForeignKey(Player, null = True, related_name = 'memberships_by')
    reason = models.TextField()

    removed_at = models.DateTimeField()
    removed_by = models.ForeignKey(Player, related_name = 'memberships_removed')
    remove_reason = models.TextField()





class Bonus(Model):
    class Meta:
        db_table = 'bonuses'

    amount = models.IntegerField()
    descr = models.TextField()
    note = models.TextField(null = True)
    at = models.DateTimeField(auto_now_add = True)

    player = models.ForeignKey(Player, related_name = 'bonuses')






class IPLog(Model):
    class Meta:
        db_table = 'iplog'

    ip = models.IPAddressField()
    active = models.BooleanField(default = True)

    came_at = models.DateTimeField(auto_now_add = True)
    left_at = models.DateTimeField(auto_now_add = True)

    player = models.ForeignKey(Player, related_name = 'iplog_records')





