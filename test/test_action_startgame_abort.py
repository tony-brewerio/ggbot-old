# -*- coding: utf-8 -*-

def test_startgame_abort():
    "test if StartGame and Abort are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    lucky = Player.get(login = 'lucky')
    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    Abort = url_map['.abort']
    Pool = url_map['.pool']


    action = Abort(room = room, player = twik)
    action()

    assert u"Нет игры" in action.privates[0][1]


    action = StartGame(room = room, player = twik, param_string = '-wtfardm')
    action()

    assert twik.current_game() == room.current_game()
    assert u"создает игру, режим => -wtfardm" in action.announces[0]
    

    action = StartGame(room = room, player = lucky)
    action()

    assert not lucky.current_game()
    assert u"Подождите, пока текущая игра не будет запущена." in action.privates[0][1]


    action = StartGame(room = room, player = twik)
    action()

    assert u"Вы уже состоите в игре." in action.privates[0][1]


    action = Pool(room = room, player = twik)()
    assert u"twik" in action.privates[0][1]


    action = Abort(room = room, player = lucky)
    action()

    assert twik.current_game()
    assert u".abort доступен только для" in action.privates[0][1]


    action = Abort(room = room, player = twik)
    action()

    assert not twik.current_game()
    assert not room.current_game()
    assert u"отменяет игру" in action.announces[0]
