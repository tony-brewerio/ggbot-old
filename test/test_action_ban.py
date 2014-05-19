# -*- coding: utf-8 -*-

def test_ban():
    "test if AddBan/RemoveBan are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    AddBan = url_map['+b']
    RemoveBan = url_map['-b']
    Timeban = url_map['+tb']

    action = RemoveBan(player = fareko, room = room, param_string = '1 ispravilsa')()
    assert u"Не найден бан #" in action.privates[0][1]

    assert imba.banned(room).count() == 0

    AddBan(player = fareko, room = room, param_string = 'imbamania lulz!!')()

    assert imba.banned(room).count() == 1

    action = RemoveBan(player = fareko, room = room, param_string = '1 ispravilsa')()
    assert u"отменяет бан #" in action.announces[0]

    assert imba.banned(room).count() == 0

    Timeban(player = fareko, room = room, param_string = 'imbamania 13d')()

    assert imba.banned(room).count() == 1

    action = RemoveBan(player = fareko, room = room, param_string = '2 ispravilsa')()
    assert u"отменяет бан #" in action.announces[0]

    assert imba.banned(room).count() == 0
