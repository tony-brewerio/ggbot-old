# -*- coding: utf-8 -*-

def test_truant():
    "test if Truant is working as it should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    StartGame = url_map['.sg']
    SignUser = url_map['.su']
    Confirm = url_map['.cf']
    Chall = url_map['.chall']
    Accept = url_map['.accept']
    Result = url_map['.r']
    AdmResult = url_map['!r']
    Truant = url_map['.t']

    assert not room.current_game()


    action = StartGame(room = room, player = twik)()
    assert room.current_game() and room.current_game() == twik.current_game()

    SignUser(room = room, player = twik, param_string = imba.login)()

    for player in Player.exclude(login = 'imbamania').\
        filter(memberships__active = True,
               memberships__room = room,
               memberships__group__name = 'player')[:10]:
        SignUser(room = room, player = twik, param_string = player.login)()

    assert room.current_game().gamestats.count() == 10

    action = Confirm(room = room, player = twik)()

    assert twik.current_game().status == 'ongoing'
    assert not room.current_game()


    old_score = imba.roomstats.get(room = room).score

    for gs in room.last_game().teams():
        Truant(room = room, player = gs.player, param_string = 'imbamania')()

    print "%s -> %s" % (old_score, imba.roomstats.get(room = room).score)
    assert imba.roomstats.get(room = room).score == old_score - 100





    sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.current_game().teams().filter(team = 'sentinel').select_related('player')]
    scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.current_game().teams().filter(team = 'scourge').select_related('player')]

    AdmResult(room = room, player = fareko, param_string = str(twik.last_game().id) + " 1")()

    new_sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'sentinel').select_related('player')]
    new_scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'scourge').select_related('player')]

    assert sum(new_sent_scores) > sum(sent_scores)
    assert sum(new_scrg_scores) < sum(scrg_scores)
