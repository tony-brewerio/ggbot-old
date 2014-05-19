# -*- coding: utf-8 -*-

#from nose import with_setup
#from test import setup_package

#@with_setup(setup_package)
def test_result():
    "test if Result is working as it should"

    from gbot.action import url_map
    from gbot.models import Player, Room
    from gbot.bot import Bot

    twik = Player.get(login = 'twik')
    fareko = Player.get(login = 'fareko')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")
    bot = Bot("SlaVe", room)

    StartGame = url_map['.sg']
    SignUser = url_map['.su']
    Confirm = url_map['.cf']
    Chall = url_map['.chall']
    Accept = url_map['.accept']
    Result = url_map['.r']
    AdmResult = url_map['!r']
    Swap = url_map['.swap']
    AdmSwap = url_map['!swap']

    assert not room.current_game()


    action = StartGame(room = room, bot = bot, player = twik)()
    assert room.current_game() and room.current_game() == twik.current_game()


    for player in Player.exclude(login = 'imbamania').\
        filter(memberships__active = True,
               memberships__room = room,
               memberships__group__name = 'player')[:10]:
        SignUser(room = room, bot = bot, player = twik, param_string = player.login)()

    assert room.current_game().gamestats.count() == 10

    action = Confirm(room = room, bot = bot, player = twik)()

    assert twik.current_game().status == 'ongoing'
    assert not room.current_game()




    assert not imba.current_game()

    for gs in twik.current_game().teams():
        Swap(room = room, bot = bot, player = gs.player, param_string = 'twik imbamania')()

    assert not twik.current_game()
    assert imba.current_game() == room.last_game()

    AdmSwap(room = room, bot = bot, player = fareko, param_string = 'imbamania twik')()

    assert twik.current_game() == room.last_game()
    assert not imba.current_game()


    sent = twik.current_game().sentinel()[0].player
    scrg = twik.current_game().scourge()[0].player
    sent_rs = room.roomstats.get(player = sent)
    scrg_rs = room.roomstats.get(player = scrg)


    action = Result(room = room, bot = bot, player = twik, param_string = '1')()

    assert twik.current_game().gamestats.get(player = twik).result == 'sentinel'

    sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.current_game().teams().filter(team = 'sentinel').select_related('player')]
    scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.current_game().teams().filter(team = 'scourge').select_related('player')]

    for gs in twik.current_game().teams():
        Result(room = room, bot = bot, player = gs.player, param_string = '1')()


    assert not twik.current_game()


    assert sent_rs.wins == (room.roomstats.get(player = sent).wins - 1)
    assert scrg_rs.loses == (room.roomstats.get(player = scrg).loses - 1)


    new_sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'sentinel').select_related('player')]
    new_scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'scourge').select_related('player')]


    assert sum(new_sent_scores) > sum(sent_scores)
    assert sum(new_scrg_scores) < sum(scrg_scores)


    AdmResult(room = room, bot = bot, player = fareko, param_string = str(twik.last_game().id) + " scourge")()


    assert sent_rs.wins == room.roomstats.get(player = sent).wins
    assert scrg_rs.loses == room.roomstats.get(player = scrg).loses

    assert sent_rs.loses == (room.roomstats.get(player = sent).loses - 1)
    assert scrg_rs.wins == (room.roomstats.get(player = scrg).wins - 1)


    new_sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'sentinel').select_related('player')]
    new_scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'scourge').select_related('player')]


    assert sum(new_sent_scores) < sum(sent_scores)
    assert sum(new_scrg_scores) > sum(scrg_scores)


    AdmResult(room = room, bot = bot, player = fareko, param_string = str(twik.last_game().id) + " 0")()


    assert sent_rs.wins == room.roomstats.get(player = sent).wins
    assert sent_rs.loses == room.roomstats.get(player = sent).loses
    assert scrg_rs.wins == room.roomstats.get(player = scrg).wins
    assert scrg_rs.loses == room.roomstats.get(player = scrg).loses


    new_sent_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'sentinel').select_related('player')]
    new_scrg_scores = [gs.player.roomstats.get(room = room).score for gs in twik.last_game().teams().filter(team = 'scourge').select_related('player')]


    assert sum(new_sent_scores) == sum(sent_scores)
    assert sum(new_scrg_scores) == sum(scrg_scores)
