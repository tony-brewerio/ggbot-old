# -*- coding: utf-8 -*-

def test_forbid_allow():
    "test if Forbid and Allow are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room, Game
    from django.db.models import Q

    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    papa = Player.get(login = 'papaDray')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    Abort = url_map['.abort']
    SignUser = url_map['.su']
    Sign = url_map['.s']
    Forbid = url_map['.forbid']
    Allow = url_map['.allow']

    assert not room.fresh_game()
    assert not fareko.current_game()


    action = StartGame(room = room, player = twik, param_string = '-wtfardm')
    action()

    assert twik.current_game() == room.fresh_game()


    action = SignUser(room = room, player = twik, param_string = 'fareko')
    action()

    assert fareko.current_game() == room.fresh_game()


    action = Forbid(room = room, player = twik, param_string = 'fareko')
    action()

    assert not fareko.current_game()


    action = SignUser(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"Доступ в игру для игрока fareko закрыт" in action.privates[0][1]
    assert not fareko.current_game()


    action = Sign(room = room, player = fareko)
    action()

    assert u"Доступ в игру для вас закрыт" in action.privates[0][1]
    assert not fareko.current_game()


    action = Allow(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"разрешает fareko доступ в игру" in action.announces[0]


    action = Sign(room = room, player = fareko)
    action()

    assert fareko.current_game() == room.current_game()


    action = Abort(room = room, player = twik)
    action()

    assert not room.current_game()
    assert not fareko.current_game()