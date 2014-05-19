# -*- coding: utf-8 -*-



def test_announce_private():
    "test if action correctly handles announce/private"

    from gbot.action import Action
    from gbot.exceptions import BotError

    class RespondingAction(Action):

        def action(self):
            self.announce('version/version')
            self.private('version/version')

    action = RespondingAction(player = 'fareko')
    action()

    assert len(action.announces) == 1
    assert len(action.privates) == 1

    msg = action.privates.pop()

    assert msg[0] == 'fareko'
    assert u"DotA bot | Garena |" in msg[1]

    assert u"DotA bot | Garena |" in action.announces.pop() 


def test_system_error():
    "test if action catches non-bot exceptions and resolves them to system/system_error"

    from gbot.action import Action
    from gbot.exceptions import BotError

    class RaisesSystemError(Action):

        def action(self):
            self.announce('version/version')
            1 / 0

    action = RaisesSystemError(player = 'fareko')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 2

    assert action.privates.pop(0) == ('fareko',
        u"Во время обработки команды произошла системная ошибка.")
    assert action.privates.pop(0) == ('fareko',
        u"Спасибо за понимание.")


def test_bot_error():
    "test if bot error is resolved correctly"

    from gbot.action import Action
    from gbot.exceptions import BotError

    class RaisesBotError(Action):

        def action(self):
            self.announce('version/version')
            raise BotError('version/version')

    action = RaisesBotError(player = 'fareko')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    msg = action.privates.pop()

    assert msg[0] == 'fareko'
    assert u"DotA bot | Garena |" in msg[1]


def test_bot_error():
    "test if errors while handling bot error resolve to system error"

    from gbot.action import Action
    from gbot.exceptions import BotError

    class RaisesBotError(Action):

        def action(self):
            self.announce('version/version')
            raise BotError('non/existing/template')

    action = RaisesBotError(player = 'fareko')
    action()

    assert len(action.announces) == 0

    assert len(action.privates) == 2
    assert action.privates.pop(0) == ('fareko',
        u"Во время обработки команды произошла системная ошибка.")
    assert action.privates.pop(0) == ('fareko',
        u"Спасибо за понимание.")


def test_membership_filter():
    "test filter deny_by_membership"

    from gbot.action import Action
    from gbot.exceptions import BotError

    class OnlyLeader(Action):

        groups = 'leader',

    assert set(['leader']) == set(OnlyLeader.groups)

    class OnlyAdmin(Action):

        groups = 'admin',

    assert OnlyAdmin.groups == ('admin',)

    from gbot.models import Player, Room

    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    action = OnlyLeader(player = gaylord, room = room)
    action()

    assert len(action.privates) == 1
    assert len(action.announces) == 0

    msg = action.privates.pop()
    assert msg[0] == gaylord
    assert msg[1] == u"Доступ запрещен. Команда доступна только членам групп => leader"
    
    fareko = Player.get(login = 'fareko')

    action = OnlyAdmin(room = room, player = fareko)
    action()

    assert len(action.privates) == 0
    assert len(action.announces) == 0
