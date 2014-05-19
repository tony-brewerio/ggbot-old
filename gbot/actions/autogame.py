from datetime import datetime, timedelta

from gbot.action import Job
from gbot.models import Game
from gbot.action import Action
from gbot.exceptions import BotError

from gbot.actions.confirm import Confirm


class stash(object):
    go = {}


class AutogameGo(Action):
    expose = '.go',

    def action(self):
        room_game = self.room.current_game()
        if not room_game:
            raise BotError('autogame/go_wait')

        if room_game.team('pool').count() < 7:
            raise BotError('autogame/go_full')

        player_game = self.player.current_game()
        if not room_game or not player_game or room_game.id != player_game.id:
            raise BotError('autogame/go_no_game')

        stash.go[self.player.id] = datetime.now()
        if len(stash.go) == 1:
            self.announce('autogame/go_begin')
        else:
            self.announce('autogame/go_go', ready=len(stash.go))


class AutogameGoCheck(Job):

    interval = 5
    bots = '1Mortal',

    def action(self):
        game = self.room.current_game()
        if not game:
            return

        pool_ids = [gs.player_id for gs in game.team('pool')]
        go = dict(
            (player_id, stash.go[player_id])
            for player_id in pool_ids
            if player_id in stash.go
        )
        if not go:
            return

        if (max(go.values()) + timedelta(seconds=60)) < datetime.now():
            self.announce('autogame/go_timeout')
            stash.go = {}
            game.delete()
            return

        if len(go) >= 10:
            stash.go = {}
            self.game = game
            self.game.confirmed_at = datetime.now()
            Confirm.confirm_regular.__func__(self)
            #
            self.announce('autogame/go_confirm')
            # we should also delete all the forbidden players now, to prevent ambiguity in swap
            self.game.gamestats.filter(team='forbidden').delete()


class AutogameStart(Job):

    interval = 5
    bots = '1Mortal',

    def action(self):
        if not self.room.current_game():
            self.start_game()
            stash.go = {}

    def start_game(self):
        game = Game.create(room=self.room, mode='-cm')
        self.announce('autogame/start_game', game=game)
