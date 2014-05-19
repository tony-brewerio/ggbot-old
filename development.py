from twisted.internet import reactor

from gbot.bot import Bot
from gbot.models import Room, Account
from gbot.protocol import GarenaRSFactory



mortal = Bot("Mortal", Room.get(name__icontains = "mortals"))

GarenaRSFactory(mortal, Account.get(login = "OSPL.MortaL"),
                write_only = False)
GarenaRSFactory(mortal, Account.get(login = "OSPL.MortaL|1"), send_kicks = True)
GarenaRSFactory(mortal, Account.get(login = "OSPL.MortaL|2"))
GarenaRSFactory(mortal, Account.get(login = "OSPL.MortaL|3"))


#god = Bot("God", Room.get(pk = 196880))

#GarenaRSFactory(god, Account.get(login = "OSPL.GoD"),
#                write_only = False, send_kicks = True)


from twisted.application.service import Application
application = Application("OSPL|Bot")


from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import LogFile

logfile = LogFile("twisted.log", "tmp/", maxRotatedFiles = 5)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)


if __name__ == '__main__':

    reactor.run()
