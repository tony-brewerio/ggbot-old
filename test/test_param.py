# -*- coding: utf-8 -*-


def test_player_param():
    "test if param.Player works"

    from gbot.action import Action
    from gbot.exceptions import BotError
    from gbot import param

    class TakesParamPlayer(Action):

        params = ['target', param.Player()]

        def action(self):
            self.announces.append(self.target.auth)


    from gbot.models import Player, Room

    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    action = TakesParamPlayer(player = gaylord, room = room)
    action()

    assert action.privates[0][1] == u"Недостаточно параметров для команды."

    action = TakesParamPlayer(player = gaylord, room = room, param_string = '1')
    action()

    assert action.announces[0] == "fareko"

    action = TakesParamPlayer(player = gaylord, room = room, param_string = 'fareko')
    action()

    assert action.announces[0] == "fareko"

    action = TakesParamPlayer(player = gaylord, room = room, param_string = 'areko')
    action()

    assert action.announces[0] == "fareko"

    action = TakesParamPlayer(player = gaylord, room = room, param_string = 'nobody')
    action()

    assert action.privates[0][1] == u"Не найден игрок по условию => nobody"

    action = TakesParamPlayer(player = gaylord, room = room, param_string = 'a')
    action()

    assert action.privates[0][1] == u"Найдено более 1-го игрока по условию => a"
    assert 'fareko' in action.privates[1][1]
    assert 'gaylord' in action.privates[1][1]
    assert 'masyoka' in action.privates[1][1]

    class ParamIsSelfPlayerByDefault(Action):

        params = ['target', param.Player(lambda action: action.player)]

        def action(self):
            self.announces.append(self.target.auth)

    action = ParamIsSelfPlayerByDefault(player = gaylord, room = room, param_string = '')
    action()


    assert action.announces[0] == "gaylord"

    action = ParamIsSelfPlayerByDefault(player = gaylord, room = room)
    action()

    assert action.announces[0] == "gaylord"



def test_group_param():
    "test if param.Player works"

    from gbot.action import Action
    from gbot.exceptions import BotError
    from gbot import param

    class TakesGroup(Action):

        params = ['group', param.Group()]

        def action(self):
            self.announces.append(self.group.name)


    from gbot.models import Player, Room

    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    action = TakesGroup(player = gaylord, room = room, param_string = 'admin')
    action()

    assert action.announces[0] == "admin"

    action = TakesGroup(player = gaylord, room = room, param_string = 'non-existing')
    action()

    assert action.privates[0][1] == u"Не найдена группа по условию => non-existing"



def test_result_param():
    "test if param.Result works"

    from gbot.action import Action
    from gbot.exceptions import BotError
    from gbot import param

    class TakesResult(Action):

        params = ['result', param.Result()]

        def action(self):
            self.announces.append(self.result)


    action = TakesResult(param_string = '0')()
    assert action.announces[0] == "draw"

    action = TakesResult(param_string = 'sentinel')()
    assert action.announces[0] == "sentinel"

    action = TakesResult(param_string = 'bla bla bla')()
    assert u"Неверный результат игры" in action.privates[0][1]



from datetime import timedelta

def test_timedelta_param():
    "test if param.Timedelta works"

    from gbot import param

    assert not param.Timedelta()(None, "as asd asd")        
    assert param.Timedelta()(None, "1d") == timedelta(days = 1)
    assert param.Timedelta()(None, "1d2d___1h-1h3d") == timedelta(days = 6, hours = 2)
    assert param.Timedelta()(None, "100d500m") == timedelta(days = 100, minutes = 500)

