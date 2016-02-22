from twisted.internet.protocol import ClientFactory, Protocol, DatagramProtocol
from twisted.internet import reactor, task
import logging
import struct
from gbot.util import split_by
from gbot.models import Account
import time, json


class LocalUDPInfo(DatagramProtocol):

    node_io_addr = ('0.0.0.0', 8124)
    bots = []
    
    def __init__(self):
        print "UDPInfo start"

    def send_json(self, obj): self.transport.write(json.dumps(obj), self.node_io_addr)

    def datagramReceived(self, data, addr):
        msg = json.loads(data)
        action = msg.get("action")
        
        print data
        
        if action == "start":
            for bot in self.bots:
                for login in [bot.logins.get(id) for id, online in bot.online.items() if online]:
                    self.player_came(bot.name, login)
                    
                    
                    
                    
    def message_received(self, room, by, body):
        self.send_json({
            "action": "message",
            "room": room,
            "by": by,
            "body": body
        })
        
    def player_came(self, room, login):
        self.send_json({
            "action": "player_came",
            "room": room,
            "login": login
        })
        
    def player_left(self, room, login):
        self.send_json({
            "action": "player_left",
            "room": room,
            "login": login
        })
            
        


#udp_info = LocalUDPInfo()
#reactor.listenUDP(8125, udp_info)



class GarenaRSUDPProtocol(DatagramProtocol):

    def __init__(self, factory):
        self.factory = factory
        self.msg_seq = int(time.time()) # because of how large unsigned int is, it is ok to do this
        self.msg_blob = "000000005c0000003f0000f800000040b40000000000000000000000ccff41007200690061006c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        self.msg_blob = self.msg_blob.decode('hex')

        print "UDP start"

        self.poll_messages()
        self.hello_everybody_lc = task.LoopingCall(self.hello_everybody).start(30, False)

        self.tries = {}
        self.resenders = {}
        self.received = []


    def poll_messages(self):
        self.factory.bot.messages.get().addCallback(self.send_message)


    def hello_everybody(self):
#        print "UDP hello => all"

        for id in [id for id, online in self.factory.bot.online.items() if online]:
            self.say_hello(id)

    def say_hello(self, id):
        addr = self.factory.bot.addr(id)
        if addr:
            hello_packet = struct.pack("< I I 8x", 2, self.factory.account.id)
            self.transport.write(hello_packet, addr)


    def datagramReceived(self, data, host_port):
        host, port = host_port

        packet_type = ord(data[0])

        if packet_type == 2:
            self.handle_hello(data)
        if packet_type == 15:
            pass
            # this is {HELLO REPLY} packet, we don't really need it, so -> ignore
            #print "UDP hello reply <= ", host_port
#
        if packet_type == 51:

            self.handle_message(data)

        if packet_type == 57:
            self.invalidate_resender(data)



    def handle_message(self, data):
        data = data[1:]


#        print len(data)
#        print data.encode('hex')

        format = "< I I I 96x I"
        unpacked = struct.unpack(format, data[:112])
        seq, from_id, to_id, length = unpacked
        msg = data[112:].decode('utf_16_le', 'ignore')

#        print self.factory.account.login + " => " + msg

#        player = self.tcp.players.get(from_id)
#        me = self.tcp.players.get(to_id)

        addr = self.factory.bot.addr(from_id)
#        print addr

        key = "%s#%s" % (from_id, seq)

        if addr and not key in self.received:
            self.received.append(key)
            reactor.callLater(10, lambda: self.received.remove(key))

#            print "{MESSAGE #%s from %s of length %s(bytes)}" % (seq, login, length)
#            print "{MSG BODY => %s}" % msg

            reply = struct.pack("< B I I 8x", 57, seq, self.factory.account.id)
            self.transport.write(reply, addr)

            reactor.callLater(0, self.factory.bot.message_received, from_id, msg, True)

#            self.send_message(me, player, u"you said => " + msg)



    def send_message(self, player_and_msg):
        self.poll_messages()
        to_player, msg = player_and_msg

        addr = self.factory.bot.addr(to_player.id)
        if addr:
            self.msg_seq += 1

            seq = self.msg_seq
            from_id = self.factory.account.id
            length = len(msg) * 2

            header = struct.pack("< B I I I", 51, seq, from_id, to_player.id)
            packet = header + self.msg_blob + struct.pack("< I", length) + msg.encode('utf_16_le', 'ignore')

            #self.transport.write(packet, addr)

            self.resenders[seq] = task.LoopingCall(self.resend_message, seq, packet, addr)
            self.tries[seq] = 0
            self.resenders[seq].start(0.4)
#            print "{MESSAGE to %s}" % to_player.login
#            print "{MSG BODY => %s}" % msg


    def invalidate_resender(self, data):
        seq = struct.unpack("<I", data[1:5])[0]
#        print "remote => i got #%s" % seq

        lc = self.resenders.get(seq)
        if lc:
            lc.stop()
            del self.resenders[seq]
            del self.tries[seq]




    def resend_message(self, seq, packet, addr):


        lc = self.resenders.get(seq)
        if lc:
            self.tries[seq] += 1
            self.transport.write(packet, addr)

#            print "sending #%s, tries: %s" % (seq, self.tries[seq])
            if self.tries[seq] > 6:
                lc.stop()
                del self.resenders[seq]
                del self.tries[seq]



    def handle_hello(self, data):
        id = struct.unpack("<I", data[4:8])[0]
        addr = self.factory.bot.addr(id)
        if addr:
            reply = struct.pack("< I I 4x I", 15, self.factory.account.id, id)
            self.transport.write(reply, addr)







class GarenaRSProtocol(Protocol):

    def __init__(self):
        self.buffer = ''

    def write(self, data): self.transport.write(data)
    def write_hex(self, data): self.write(data.decode('hex'))

    def connectionMade(self):
        self.log = logging.getLogger("GRSP[%s]" % self.factory.account.login)
        self.log.info(u"connection made, sending auth packet")

        self.write_hex(self.factory.packet)
        
        self.log.info(u"issuing disconnect in 45 seconds if Garena did not respond with WELCOME")
        self.timeout_deferred = reactor.callLater(45, self.timeout)
        
    def timeout(self):
        self.log.error(u"Garena did not send WELCOME packet in 45 seconds, dropping connection now")
        self.transport.loseConnection()

    def dataReceived(self, data):
        self.buffer += data
        self.decodeHeader()

    def decodeHeader(self):
        if len(self.buffer) >= 5:
            header = struct.unpack("< I B", self.buffer[:5])
            if len(self.buffer) >= header[0]+4:
                packet = self.buffer[5:header[0]+4]
                self.buffer = self.buffer[header[0]+4:]
                if len(self.buffer) >= 5:
                    reactor.callLater(0, self.decodeHeader)
                self.decodePacket(header[1], packet)

    def decodePacket(self, packet_type, data):
        if self.factory.write_only and packet_type != 48: return

        getattr(self, 'handle_' + {
            34: 'player_came',
            35: 'player_left',
            37: 'message',
            44: 'userlist',
            48: 'welcome'
        }.get(packet_type, 'non_existing'), lambda data: None)(data)


    def handle_non_existing(self, data):
        self.log.info(u"??? -> %s", data.encode('hex'))


    def handle_player_left(self, data):
        id = struct.unpack("< I", data)[0]
        self.factory.bot.player_left(id)


    def handle_player_came(self, data):
        format = "< I 15s 6x 1B 2x 4B 32x"
        unpacked = struct.unpack(format, data)
        id = unpacked[0]
        login = unicode(unpacked[1].rstrip(chr(0)), 'ascii', 'ignore')
        ip = "%s.%s.%s.%s" % unpacked[3:]
        lvl = unpacked[2]
        port = struct.unpack(">H", data[40:42])[0]
        if not Account.get_or(pk = id):
            self.factory.bot.player_came(id, login, ip, port, lvl)
        else:
            self.log.info(u"%s is bot's account -> do nothing", login)

        #if hasattr(self.factory, 'udp_protocol'):
        #    self.factory.udp_protocol.say_hello(id)


    def handle_userlist(self, data):
        self.log.info(u"cancelling TIMEOUT")
        self.factory.connection = self
        timeout_deferred = getattr(self, 'timeout_deferred', None)
        if timeout_deferred and timeout_deferred.active:
            timeout_deferred.cancel()
            del self.timeout_deferred


        self.log.info(u"got userlist")
        for user_data in [ud for ud in split_by(data[8:], 64) if len(ud) == 64]:
            self.handle_player_came(user_data)



    def handle_message(self, data):
        id = struct.unpack("<I", data[4:8])[0]
        message = unicode(data[12:], 'utf_16_le', 'ignore').strip()

        reactor.callLater(0, self.factory.bot.message_received, id, message)


    def handle_welcome(self, data):
        self.log.info(u"got WELCOME")
        self.log.info(u"cancelling TIMEOUT")

        self.factory.connection = self
        timeout_deferred = getattr(self, 'timeout_deferred', None)
        if timeout_deferred and timeout_deferred.active:
            try:
                timeout_deferred.cancel()
            except:
                pass
            del self.timeout_deferred




class GarenaRSFactory(ClientFactory):
    protocol = GarenaRSProtocol

    def __init__(self, bot, account, write_only = True,
                 send_kicks = False, send_anns = True, send_pvts = True):
        self.bot = bot
        self.account = account
        self.write_only = write_only
        self.connection = None

        self.log = logging.getLogger("GRSF[%s:%s]" % (bot.name, account.login))
        self.log.info(u"initialized")

        self.packet = account.packet.replace("{roomid}",
                struct.pack("< I", bot.room.id).encode('hex'))

        # deferreds
        if send_anns: self.bot.announces.get().addCallback(self.send_announce)
        if send_pvts: self.bot.privates.get().addCallback(self.send_private)
        if send_kicks: self.bot.kicks.get().addCallback(self.send_kick)

        #only now enable udp for ospl.slave
        #if account.port > 15000:
        #    self.udp_protocol = GarenaRSUDPProtocol(self)
        #    self.udp = reactor.listenUDP(account.port, self.udp_protocol, interface = '212.154.211.111')
        #else:
        #    self.udp = None


        self.connect()


    def connect(self):
        self.log.info(u"issuing roomserver connection")
        reactor.connectTCP(self.bot.room.ip, 8687, self)

    def reconnect(self):
        self.log.info(u"issuing reconnect in 5 seconds")
        self.connection = None
        if not self.write_only:
            self.log.info(u"lost connection on reading bot, moving ip_list to stale")
            for id in self.bot.ip_list.keys():
                reactor.callLater(0, self.bot.player_left, id)

        reactor.callLater(5, self.connect)
    


    def startedConnecting(self, connector):
        self.log.info(u"started connecting")


    def clientConnectionLost(self, connector, reason):
        self.log.error(u"connection lost, reason: %s", reason)
        self.reconnect()

    def clientConnectionFailed(self, connector, reason):
        self.log.error("uconnection failed, reason: %s", reason)
        self.reconnect()




    def send_kick(self, (player_id, reason)):
        self.kick_deferred = self.bot.kicks.get().addCallback(self.send_kick)
        if self.connection:
            self.log.debug(u"doing kick => %s @ %s", player_id, reason)
            format = "< I b I I I"
            packet = struct.pack(format, len(reason) + 13, 40, self.account.id,
                                 player_id, len(reason)) + reason.encode('ascii', 'ignore')
            self.connection.write(packet)

            # remove 15 min ban, that happens after player is kicked
            player_login = self.bot.logins.get(player_id, u'').encode('ascii', 'ignore')
            if player_login and False:
                self.log.debug(u"removing 15min ban => %s", player_login)

                packet = struct.pack("< I b I", len(player_login) + 10, 120, self.bot.room.id) + \
                    player_login + ("\0" * 5)
                self.connection.write(packet)            

        else:
            self.log.error(u"kick : no connection")



    def send_private(self, (player_id, message)):
        reactor.callLater(0.55, lambda: self.bot.privates.get().addCallback(self.send_private))
        if self.connection:
            format = "< I b I I"
            packet = struct.pack(format, len(message) * 2 + 9, 127,
                                 self.account.id,
                                 player_id) + message.encode('utf_16_le', 'ignore')
            self.connection.write(packet)
        else:
            self.log.error(u"pvt : no connection")


    def send_announce(self, message):
        reactor.callLater(1.1, lambda: self.bot.announces.get().addCallback(self.send_announce))
        if self.connection:
            self.log.debug(u"ANN -> %s", message)
            format = "< I b I"
            packet = struct.pack(format, len(message) * 2 + 5, 48,
                                 self.bot.room.id) + message.encode('utf_16_le', 'ignore')
            self.connection.write(packet)
        else:
            self.log.error(u"ann : no connection")






