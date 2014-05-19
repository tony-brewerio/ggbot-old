from socket import inet_ntoa
import struct

#import test
#test.install()

from sqlalchemy.ext.sqlsoup import SqlSoup
db = SqlSoup('sqlite:////home/fareko/gspam/roomEN.dat')

rows = list(db.engine.execute("""
    select
        rt.RoomId, rt.RoomName, rst.IP
    from
        roomtab rt, roomservertab rst
    where
        rst.ServerId = rt.ServerId 
    order by
        rt.RoomName desc
"""))

from gbot.models import Room, Account

for id, name, ip in rows:
    print "#%s -> %s" % (id, name)
    Room.create(id = id, name = name, ip = inet_ntoa(struct.pack("<i", ip)))
