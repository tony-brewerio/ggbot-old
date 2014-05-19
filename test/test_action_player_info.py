# -*- coding: utf-8 -*-

def test_player_info():
    "test if PlayerInfo is working as it should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    PlayerInfo = url_map['.i']


    action = PlayerInfo(player = fareko, room = room)
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 2

    assert u"fareko : score => " in action.privates[0][1]
    assert u"admin" in action.privates[1][1]



