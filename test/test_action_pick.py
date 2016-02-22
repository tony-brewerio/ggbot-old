# -*- coding: utf-8 -*-

def test_pick():
    "test if Pick is working as it should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    twik = Player.get(login = 'twik')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    Chall = url_map['.chall']
    Accept = url_map['.accept']
    SignUser = url_map['.su']
    Confirm = url_map['.cf']
    Pick = url_map['.pick']

    assert not twik.current_game()
    assert not imba.current_game()
    assert not room.current_game()


    action = Chall(room = room, player = twik, param_string = 'imbamania')
    action()

    assert room.current_game()


    action = Accept(room = room, player = imba)()
    assert u"imbamania принимает вызов twik" in action.announces[0]


    for player in Player.filter(memberships__active = True,
                                memberships__room = room,
                                memberships__group__name = 'player'):
        SignUser(room = room, player = twik, param_string = player.auth)()

    action = Confirm(room = room, player = twik)()
    assert twik.current_game().status == 'pick'


    sentinel_captain = twik.current_game().gamestats.select_related('player').\
        get(team = 'sentinel', captain = True).player
    scourge_captain = twik.current_game().gamestats.select_related('player').\
        get(team = 'scourge', captain = True).player


    assert sentinel_captain == twik.current_game().picker()

    pool = list(twik.current_game().gamestats.filter(team = 'pool').select_related('player'))

    action = Pick(room = room, player = scourge_captain, param_string = pool[0].player.auth)()
    assert u"Не ваша очередь пикать" in action.privates[0][1]

    for i in xrange(8):
        action = Pick(room = room, player = twik.current_game().picker(),
                      param_string = pool.pop().player.auth)()

    assert twik.current_game().status == 'ongoing'


    twik.current_game().delete()
    assert not twik.current_game()

