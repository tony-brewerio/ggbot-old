# -*- coding: utf-8 -*-

def test_regular_confirm():
    "test if Confirm is working as it should on REGULAR games"

    from gbot.action import url_map
    from gbot.models import Player, Room

    twik = Player.get(login = 'twik')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    SignUser = url_map['.su']
    Confirm = url_map['.cf']
    Chall = url_map['.chall']
    Accept = url_map['.accept']
    
    assert not room.current_game()
    
   
    action = StartGame(room = room, player = twik)()
    assert room.current_game() == twik.current_game()
    assert room.current_game().gamestats.count() == 1


    for player in Player.filter(memberships__active = True,
                                memberships__room = room,
                                memberships__group__name = 'player')[:10]:
        SignUser(room = room, player = twik, param_string = player.auth)()

    assert room.current_game().gamestats.count() == 10

    action = Confirm(room = room, player = twik)()
    
    assert twik.current_game().status == 'ongoing'
    assert not room.current_game()

        
    twik.current_game().delete()
    assert not twik.current_game()


    Chall(room = room, player = twik, param_string = 'imbamania')()
    Accept(room = room, player = imba)()
    
    assert room.current_game() == twik.current_game()
    assert room.current_game().gamestats.count() == 2
   
    for player in Player.filter(memberships__active = True,
                                memberships__room = room,
                                memberships__group__name = 'player'):
        SignUser(room = room, player = twik, param_string = player.auth)()


    action = Confirm(room = room, player = twik)()

    assert twik.current_game().status == 'pick'
    assert len(action.announces) == 3
    

    twik.current_game().delete()
    assert not twik.current_game()
