# -*- coding: utf-8 -*-

def test_warn():
    "test if AddWarn/RemoveWarn are working as they should"

    from gbot.action import url_map
    from gbot.models import Player, Room

    fareko = Player.get(login = 'fareko')
    imba = Player.get(login = 'imbamania')
    room = Room.get(name = "0SPL-Allstars Slaves Room")

    AddWarn = url_map['+w']
    Censure = url_map['.c']
    RemoveWarn = url_map['-w']

    action = RemoveWarn(player = fareko, room = room, param_string = '100 ispravilsa')()
    assert u"Не найден варн #" in action.privates[0][1]

    assert imba.warns.filter(type = 'noob', active = True).count() == 0

    AddWarn(player = fareko, room = room, param_string = 'imbamania noob RLY!')()

    assert imba.warns.filter(type = 'noob', active = True).count() == 1

    action = RemoveWarn(player = fareko, room = room,
                        param_string = '%s ispravilsa' % imba.warns.latest('at').id)()
    assert u"отменяет варн #" in action.announces[0]

    assert imba.warns.filter(type = 'noob', active = True).count() == 0


