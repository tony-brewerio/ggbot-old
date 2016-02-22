from twisted.internet.defer import DeferredQueue
from gbot.models import Player, Group, IPLog
from gbot.action import url_map
import logging
from twisted.internet import reactor
from django.db import transaction
#from gbot.protocol import udp_info
from datetime import datetime


class Bot(object):

    bot_by_name = {}

    def update_iplog(self):
        reactor.callLater(60, self.update_iplog)

        # get list of online player's ids
        ids = [id for id, online in self.online.items() if online]

        # update iplog!
        IPLog.filter(player__in = ids, active = True).\
            update(left_at = datetime.now())


    def __str__(self): return self.name

    def __init__(self, name, room):
        self.log = logging.getLogger("B[%s]" % name)
        self.bot_by_name[name] = self

        self.name = name
        self.room = room
        self.ip_list = {}
        self.port_list = {}
        self.online = {}
        self.logins = {}

        self.log.info(u"__init__")

        self.announces = DeferredQueue()
        self.privates = DeferredQueue()
        self.kicks = DeferredQueue()

        self.messages = DeferredQueue()

        #udp_info.bots.append(self)

        reactor.callLater(60, self.update_iplog)

    
    def ip(self, player): return self.ip_list.get(player.id, None)
    def addr(self, id):
        if id in self.ip_list:
            return (self.ip_list.get(id), self.port_list.get(id))
    def is_online(self, id): return self.online.get(id)

    @transaction.commit_on_success    
    def player_left(self, id):
        player = Player.get_or(pk = id)    
        self.log.info(u"player left -> %s", player)

      

        if player:
            #udp_info.player_left(self.name, player.login)
            pass
        else:
            self.log.warn(u"player left -> unknown of id %s", id)
            return

        self.online[id] = False

        # ensure no active iplog records left
        player.iplog_records.filter(active = True).update(
            active = False, left_at = datetime.now()
        )

        current_game = self.room.current_game()
        
        if player and current_game:
            if player in [current_game.created_by, current_game.accepted_by]:
                current_game.delete()
                self.announces.put("%s leaves the room -> Game #%s is aborted" % (player, current_game.id))    
            elif current_game.status == 'fresh' and \
                current_game.gamestats.filter(team = 'pool', player = player).count() == 1:
                current_game.gamestats.filter(player = player).delete()
                self.announces.put("%s leaves the room -> and is dropped from pool" % player)    

    @transaction.commit_on_success
    def player_came(self, id, login, ip, port, lvl):
        self.log.info(u"player came -> %s : %s @ %s", id, login, ip)

        #udp_info.player_came(self.name, login)
        
        self.ip_list[id] = ip
        self.port_list[id] = port
        self.online[id] = True
        self.logins[id] = login

        player, created = Player.get_or_create(pk = id)
        player.login = login
        player.save()
        

        if created:
            player.roomstats.create(room_id = 983032)
            player.roomstats.create(room_id = 983033)

        # kickin' if lvl < 15
        if lvl < 15:
            return self.kicks.put((player.id, "lvl < 15"))

        if not player.member_of(self.room, 'player'):
            player.memberships.create(room=self.room, group=Group.get(name='player'), reason='autovouch')

        if player.memberships.filter(room = self.room, active = True).count() == 0:
            return self.kicks.put((player.id, "not vouched"))

        # kickin' if banned
        bans = player.banned(self.room)
        if bans:
            return self.kicks.put((player.id, "ban #%s" % bans[0].id))

        # ensure no active ones
        player.iplog_records.filter(active = True).update(active = False)
        # create new iplog record
        player.iplog_records.create(ip = ip)


    def message_received(self, id, message, reply_to_msgbox = False):
        player = Player.get(pk = id)
        self.log.debug(u"MSG <- %s : %s", player, message)

        #udp_info.message_received(self.name, player.login, message)

        if player.memberships.filter(room=self.room, active=True).count() == 0:
            return self.kicks.put((player.id, "not vouched"))

        command = message.strip().split(None, 1)
        if command and command[0] in url_map:
            action = url_map[command[0]](room = self.room, player = player, bot = self,
                                         reply_to_msgbox = reply_to_msgbox,
                                         param_string = (command[1:] or [''])[0])()

            for announce in action.announces:
                self.announces.put(announce)

            if reply_to_msgbox:
                msgs = []
                msgs_to = None
                for pvt in [pvt for pvt in action.privates if pvt[0].id == id]:
                    action.privates.remove(pvt)
                    msgs.append(pvt[1])
                    msgs_to = pvt[0]

                if msgs_to:
                    self.messages.put((msgs_to, "\n".join(msgs)))


            for target, message in action.privates:
                self.log.info(u"PVT @ %s -> %s", target, message)
                self.privates.put((target.id, message))

            for target, reason in action.kicks:
                self.kicks.put((target.id, reason))
                
                
                
