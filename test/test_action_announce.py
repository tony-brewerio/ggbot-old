# -*- coding: utf-8 -*-

def test_bot_error():
    "test if Annnounce works as it should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    action = url_map['!ann'](player = fareko, room = room, param_string = 'yay!')
    action()

    assert len(action.announces) == 1
    assert len(action.privates) == 0

    assert action.announces[0] == u"fareko => yay!"
