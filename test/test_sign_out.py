# -*- coding: utf-8 -*-

def test_sign_out():
    "test if Sign and Out are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    Abort = url_map['.abort']
    Sign = url_map['.s']
    Out = url_map['.out']

    assert not room.fresh_game()
    assert not fareko.current_game()


    action = Out(room = room, player = fareko)
    action()

    assert u"Неоткуда" in action.privates[0][1]


    action = Sign(room = room, player = fareko)
    action()

    assert not fareko.current_game()
    assert u"Нет игры" in action.privates[0][1]


    action = StartGame(room = room, player = twik, param_string = '-wtfardm')
    action()

    assert twik.current_game() == room.fresh_game()


    action = Out(room = room, player = twik)
    action()

    assert twik.current_game() == room.fresh_game()
    assert u"не может выйти командой .out" in action.privates[0][1]


    action = Sign(room = room, player = fareko)
    action()

    assert fareko.current_game() == room.fresh_game()
    assert u"присоединяется к игре" in action.announces[0]


    action = Out(room = room, player = fareko)
    action()

    assert not fareko.current_game()
    assert u"fareko выходит из пула" in action.announces[0]


    action = Abort(room = room, player = twik)
    action()

    assert not room.current_game()
    assert not fareko.current_game()
