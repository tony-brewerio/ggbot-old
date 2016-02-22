from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import logging
import socket
import struct
import zlib

from Crypto import Random
from Crypto.Cipher import AES
from django.conf import settings
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory, connectionDone, Protocol
from twisted.protocols.basic import IntNStringReceiver

from ggbot.utils import split_by


class GarenaLeague(object):
    log = logging.getLogger(__name__ + '.league')

    def __init__(self, league, rsa_encrypt):
        self.league = league
        self.rsa_encrypt = rsa_encrypt
        self.league_room = league.room
        self.clients = [GarenaClient(self, account) for account in league.accounts.all()]

    def start(self):
        for client in self.clients:
            client.auth()


class GarenaClient(object):
    log = logging.getLogger(__name__ + '.client')

    def __init__(self, league, account):
        self.league = league
        self.account = account
        self.auth_factory = GarenaAuthFactory(self)
        self.auth_info = None
        self.room_factory = GarenaRoomFactory(self)

    def auth(self):
        self.auth_factory.start()

    def on_auth_info(self, info):
        self.auth_info = info
        self.auth_factory.stop()
        self.room_factory.start()


class GarenaAuthProtocol(Protocol):
    log = logging.getLogger(__name__ + '.auth')

    def __init__(self, factory, account, rsa_encrypt):
        self.factory = factory
        self.account = account
        self.rsa_encrypt = rsa_encrypt
        self.connection_timeout_timer = None
        self.buffer = b''
        self.aes_key = Random.get_random_bytes(32)
        self.aes_iv = Random.get_random_bytes(16)

    def aes_encrypt(self, packet):
        return AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv).encrypt(packet)

    def aes_decrypt(self, packet):
        return AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv).decrypt(packet)

    def connectionMade(self):
        self.log.info('[%s] connection made', self.account.login)
        self.factory.connection = self
        self.connection_timeout_timer = reactor.callLater(10, self.connection_timeout)
        self.send_key()

    def connectionLost(self, reason=connectionDone):
        self.log.info('[%s] connection lost - %s', self.account.login, reason)
        self.factory.connection = None
        if self.connection_timeout_timer and not self.connection_timeout_timer.called:
            self.connection_timeout_timer.cancel()

    def dataReceived(self, data):
        self.buffer += data
        if len(self.buffer) >= 4:
            # packets from auth server always have least significant bit of fourth byte set to one
            # which means if we have packet of 16 bytes, packet length header will be 0x10000001 and not 0x10000000
            # that's why I cannot simply use builtin IntNStringReceiver
            # official client will send every AES encrypted packet with this bit set, but not the very first RSA one
            packet_length = struct.unpack('<H', self.buffer[:2])[0]
            if len(self.buffer) >= 4 + packet_length:
                self.buffer, packet = self.buffer[4 + packet_length:], self.buffer[4:4 + packet_length]
                self.packet_received(self.aes_decrypt(packet))

    def connection_timeout(self):
        self.log.info('[%s] login timed out', self.account.login)
        self.transport.loseConnection()

    def packet_received(self, packet):
        if len(packet) > 0:
            if packet[0] == b'\xAE':
                self.log.info('[%s] key exchange ok', self.account.login)
                self.send_login()
            elif packet[0] == b'\x45':
                self.log.info('[%s] login ok', self.account.login)
                # this is a special info block that server sends in response to successful login
                # later it is used to connect to room servers
                self.factory.client.on_auth_info(packet[9:101])
            elif packet[0] == b'\xF9':
                self.log.info('[%s] expected packet 0xF9', self.account.login)
            else:
                self.log.warning('[%s] unexpected packet: %s', self.account.login, packet.encode('hex'))
        else:
            self.log.warning('[%s] empty packet received', self.account.login)
            self.transport.loseConnection()

    def send_packet(self, packet, aes=True):
        self.transport.write(
            struct.pack('<H', len(packet)) +
            (b'\x00\x01' if aes else b'\x00\x00') +
            (self.aes_encrypt(packet) if aes else packet)
        )

    def send_key(self):
        self.log.info('[%s] sending key', self.account.login)
        packet = b'\xAD'  # packet id
        packet += b'\0'  # official client sends zero byte here
        # official client sends 0x0FF0 there
        packet += self.rsa_encrypt(self.aes_key + self.aes_iv + b'\x0F\xF0')
        self.send_packet(packet, aes=False)

    def send_login(self):
        self.log.info('[%s] sending login request', self.account.login)
        packet = b'\x21'  # packet id
        packet += b'\0\0\0\0'  # official client always sends four zero bytes here
        packet += self.account.login.encode('utf-8').ljust(16, b'\0')  # login padded with zero bytes
        packet += b'\0\0\0\0'  # official client always sends four zero bytes here
        packet += struct.pack('<I', 32)  # size of password hash in bytes
        packet += hashlib.md5(self.account.get_password()).hexdigest()
        packet += b'\x00\x01'  # no idea, some kind of flag prob
        # official client sends here ip address of first non-loopback connection it finds, which it bind p2p socket to
        # I'm pretty sure that this data is useless to the server anyway, since clients discover each other via udp
        packet += socket.inet_aton('127.0.0.1')  # don't want to bother with proper ip address detection
        packet += struct.pack('>H', 1513)  # this is default port used by official client
        packet += b'\0' * 132  # official client adds 132 zero bytes here
        packet = packet.ljust(208, b'\x07')  # pad to /16 for aes, 0x07 is what official client uses
        self.send_packet(packet)


class GarenaAuthFactory(ReconnectingClientFactory):
    log = logging.getLogger(__name__ + '.authfact')

    def __init__(self, client):
        self.client = client
        self.connection = None

    def buildProtocol(self, addr):
        return GarenaAuthProtocol(self, self.client.account, self.client.league.rsa_encrypt)

    def start(self):
        self.stop()
        self.resetDelay()
        reactor.connectTCP(settings.GGBOT['auth']['server'], settings.GGBOT['auth']['port'], self)

    def stop(self):
        self.stopTrying()
        if self.connection is not None:
            self.connection.transport.loseConnection()


class GarenaRoomProtocol(IntNStringReceiver):
    log = logging.getLogger(__name__ + '.room')

    structFormat = '<I'
    prefixLength = 4

    def __init__(self, factory, account, info):
        self.factory = factory
        self.account = account
        self.info = info
        self.connection_timeout_timer = None
        self.callbacks = {
            b'\x30': self.on_welcome,
            b'\x2C': self.on_members,
            b'\x22': self.on_player_join,
            b'\x23': self.on_player_leave,
            # b'\x25': self.on_message,
            # b'\x3A': self.on_playing_on,
            # b'\x39': self.on_playing_off,
        }

    def connectionMade(self):
        self.log.info('[%s] connection made', self.account.login)
        self.factory.connection = self
        self.connection_timeout_timer = reactor.callLater(10, self.connection_timeout)
        self.send_join()

    def connectionLost(self, reason=connectionDone):
        if reason is connectionDone:
            self.log.info('[%s] connection lost cleanly', self.account.login)
        else:
            self.log.info('[%s] connection lost - %s', self.account.login, reason)
        self.factory.connection = None
        if self.connection_timeout_timer and not self.connection_timeout_timer.called:
            self.connection_timeout_timer.cancel()
            self.connection_timeout_timer = None

    def stringReceived(self, packet):
        if len(packet) > 0:
            callback = self.callbacks.get(packet[0])
            if callback:
                callback(packet[1:])
            else:
                self.log.warning('[%s] unknown packet - %s', self.account.login, packet.encode('hex'))
        else:
            self.log.warning('[%s] empty packet received', self.account.login)
            self.transport.loseConnection()

    def connection_timeout(self):
        self.log.info('[%s] login timed out', self.account.login)
        self.transport.loseConnection()

    def send_join(self):
        self.log.info('[%s] sending join', self.account.login)
        packet = b'\x22'
        packet += struct.pack('<I', self.factory.client.league.league_room.id)
        packet += b'\x01\x00\x00\x00'  # official client sends this
        # info block is compressed with deflate with checksum attached
        # we throw out 2 byte zlib header and checksum
        packet_info = zlib.compress(self.info)
        packet_info_crc = struct.pack('<i', zlib.crc32(self.info))
        # add these two to packet
        packet += struct.pack('<I', len(packet_info) + len(packet_info_crc))
        packet += packet_info_crc
        packet += packet_info
        # room password, if any
        # note that official client does not use all 15 bytes for password
        #
        packet += '1234567890'.encode('utf-8').ljust(15, b'\0')
        # final block with user password
        packet += hashlib.md5(self.account.get_password()).hexdigest()
        packet += b'\0' * 2
        self.sendString(packet)

    def on_welcome(self, packet):
        self.log.info('[%s] connected to room server', self.account.login)
        if self.connection_timeout_timer and not self.connection_timeout_timer.called:
            self.connection_timeout_timer.cancel()
            self.connection_timeout_timer = None

    def on_members(self, packet):
        self.log.info('[%s] got list of connected players', self.account.login)
        for user_data in [ud for ud in split_by(packet[8:], 64) if len(ud) == 64]:
            self.on_player_join(user_data)

    def on_player_join(self, packet):
        player = {
            'id': struct.unpack('<I', packet[0:4])[0],
            'login': unicode(packet[4:20].rstrip(b'\0'), 'utf-8', 'ignore'),
            'country': unicode(packet[20:22], 'utf-8', 'ignore'),
            'lvl': struct.unpack('<B', packet[25])[0],
            'playing': packet[27] == b'\x01',
            'ip': socket.inet_ntoa(packet[28:32]),
            'port': struct.unpack('>H', packet[40:42])[0],
        }
        self.log.info('[%s] player joined the room %s', self.account.login, player)

    def on_player_leave(self, packet):
        self.log.info('[%s] player left the room', self.account.login)


class GarenaRoomFactory(ReconnectingClientFactory):
    log = logging.getLogger(__name__ + '.roomfact')

    def __init__(self, client):
        self.client = client
        self.connection = None

    def buildProtocol(self, addr):
        return GarenaRoomProtocol(self, self.client.account, self.client.auth_info)

    def start(self):
        self.stop()
        self.resetDelay()
        reactor.connectTCP(self.client.league.league_room.ip, settings.GGBOT['room']['port'], self)

    def stop(self):
        self.stopTrying()
        if self.connection is not None:
            self.connection.transport.loseConnection()
