# -*- coding: utf-8 -*-

def test_membership():
    "test if AddMembership and RemoveMembership work as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    gaylord = Player.get(login = 'gaylord')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    AddMembership = url_map['+m']
    RemoveMembership = url_map['-m']

    
    action = AddMembership(player = fareko, room = room,
                           param_string = 'fareko admin')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert action.privates[0][1] == u"fareko уже состоит в группе admin"


    assert not gaylord.member_of(room, 'moder')
    action = AddMembership(player = fareko, room = room,
                           param_string = 'gaylord moder')
    action()
    assert gaylord.member_of(room, 'moder')


    assert len(action.announces) == 2
    assert len(action.privates) == 0    

    assert action.announces[0] == u"fareko дает gaylord членство в группе moder"


    action = AddMembership(player = gaylord, room = room,
                           param_string = 'gaylord admin')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert action.privates[0][1] == u"Только админы могут назначать админов и модеров."


    action = RemoveMembership(player = fareko, room = room,
                              param_string = 'gaylord admin')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert action.privates[0][1] == u"gaylord не состоит в группе admin"


    action = RemoveMembership(player = gaylord, room = room,
                              param_string = 'fareko admin')
    action()

    assert len(action.announces) == 0
    assert len(action.privates) == 1

    assert action.privates[0][1] == u"Только админы могут снимать админов и модеров."


    assert gaylord.member_of(room, 'moder')
    action = RemoveMembership(player = fareko, room = room,
                              param_string = 'gaylord moder')
    action()
    assert not gaylord.member_of(room, 'moder')


    assert len(action.announces) == 2
    assert len(action.privates) == 0

    assert action.announces[0] == u"fareko забирает у gaylord членство в группе moder"
