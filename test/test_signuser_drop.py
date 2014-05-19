# -*- coding: utf-8 -*-

def test_signuser_drop():
    "test if SignUser and Drop are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    papa = Player.get(login = 'papaDray')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    Abort = url_map['.abort']
    SignUser = url_map['.su']
    Drop = url_map['.drop']

    assert not room.fresh_game()
    assert not fareko.current_game()


    action = Drop(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"Неоткуда выбросить игрока" in action.privates[0][1]


    action = SignUser(room = room, player = twik, param_string = 'fareko')
    action()

    assert not fareko.current_game()
    assert u"Нет игры" in action.privates[0][1]


    action = SignUser(room = room, player = twik, param_string = 'gaylord')
    action()

    assert u"не завоучен" in action.privates[0][1]


    action = StartGame(room = room, player = twik, param_string = '-wtfardm')
    action()

    assert twik.current_game() == room.fresh_game()


    action = Drop(room = room, player = twik, param_string = 'twik')
    action()

    assert u"не может быть выброшен командой .drop" in action.privates[0][1]


    action = Drop(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"не состоит в текущей игре" in action.privates[0][1]


    action = SignUser(room = room, player = twik, param_string = 'twik')
    action()

    assert u"уже состоит в игре" in action.privates[0][1]


    action = SignUser(room = room, player = papa, param_string = 'fareko')
    action()

    assert u".su может использовать только игрок" in action.privates[0][1]
    assert not fareko.current_game()


    action = SignUser(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"добавляет в пул" in action.announces[0]
    assert fareko.current_game() == room.current_game()


    action = Drop(room = room, player = papa, param_string = 'fareko')
    action()

    assert u"только игрок, создавший игру и капы чалла" in action.privates[0][1]
    assert fareko.current_game() == room.current_game()


    action = SignUser(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"уже состоит в игре" in action.privates[0][1]


    action = Drop(room = room, player = twik, param_string = 'fareko')
    action()

    assert u"убирает из пула" in action.announces[0]
    assert not fareko.current_game()


    action = Abort(room = room, player = twik)
    action()

    assert not room.current_game()
    assert not fareko.current_game()
