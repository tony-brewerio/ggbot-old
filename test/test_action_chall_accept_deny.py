# -*- coding: utf-8 -*-

def test_chall_accept_deny():
    "test if Chall and Accept and Deny are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    dray = Player.get(login = 'papaDray')
    twik = Player.get(login = 'twik')
    imba = Player.get(login = 'imbamania')
    fareko = Player.get(login = 'fareko')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    Chall = url_map['.chall']
    Abort = url_map['.abort']
    Accept = url_map['.accept']
    Deny = url_map['.deny']

    assert not twik.current_game()
    assert not imba.current_game()
    assert not room.current_game()


    action = Chall(room = room, player = twik, param_string = 'twik')
    action()

    assert not room.current_game()
    assert u"Нельзя чаллить самого себя" in action.privates[0][1]


    action = Chall(room = room, player = twik, param_string = 'imbamania')
    action()

    assert room.current_game()
    assert room.current_game().type == 'chall'
    assert room.current_game().status == 'chall'
    assert room.current_game().accepted_by == imba
    assert room.current_game().gamestats.get(captain = True, team = 'sentinel')
    assert room.current_game().gamestats.get(captain = True, team = 'scourge')


    action = Accept(room = room, player = dray)()
    assert u"Нет чалла." in action.privates[0][1] 

    action = Deny(room = room, player = twik)()
    assert u"Нет чалла." in action.privates[0][1] 


    action = Accept(room = room, player = imba)()
    assert u"imbamania принимает вызов twik" in action.announces[0] 
    assert room.current_game().status == 'fresh'
    
    
    action = Abort(room = room, player = twik)
    action()

    assert not twik.current_game()
    assert not room.current_game()    


    action = Chall(room = room, player = imba, param_string = 'twik')()
    
    action = Deny(room = room, player = twik)()
    assert u"twik отклоняет вызов imbamania" in action.announces[0] 
    assert not room.current_game()
    
