# -*- coding: utf-8 -*-

def test_vouch():
    "test if Vouch and Unvouch work as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    Vouch = url_map['+v']
    Unvouch = url_map['-v']


    assert not gaylord.member_of(room, 'player')
    action = Vouch(player = fareko, room = room,
                   param_string = 'gaylord for lulz')
    action()
    assert gaylord.member_of(room, 'player')

    assert len(action.announces) == 2
    assert len(action.privates) == 0

    assert u"for lulz" in action.announces[1]


    action = Vouch(player = fareko, room = room,
                   param_string = 'gaylord for lulz')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert u"уже завоучен" in action.privates[0][1]


    assert gaylord.member_of(room, 'player')
    action = Unvouch(player = fareko, room = room,
                     param_string = 'gaylord for lulz')
    action()
    assert not gaylord.member_of(room, 'player')

    assert len(action.announces) == 2
    assert len(action.privates) == 0

    assert u"for lulz" in action.announces[1]


    action = Unvouch(player = fareko, room = room,
                     param_string = 'gaylord for lulz')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert u"не завоучен" in action.privates[0][1]
