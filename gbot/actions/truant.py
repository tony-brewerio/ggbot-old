from gbot.action import Action
from gbot.exceptions import BotError
from gbot import param
from django.db.models import F
from gbot.models import Player
from gbot.storage import storage

class Truant(Action):

    expose = '.t', '.truant'
    groups = 'player',
    params = ['target', param.Player()]

    def action(self):
        self.game = self.player.current_game()

        if not (self.game and self.game.status == 'ongoing'):
            raise BotError('no_game')
        if self.target.current_game() != self.game:
            raise BotError('not_on_game')


        key = 'game:%s:truant[%s]' % (self.game.id, self.target.id)
        self.votes = storage.get_set(key, [])

        if self.player.id in self.votes:
            raise BotError('already')
        self.votes.append(self.player.id)

        self.announce('vote')

        if len(self.votes) >= (self.game.teams_size() / 2) + 1:
            del storage[key]
            self.game.gamestats.filter(player = self.target).update(truanted = True)
            self.truant = self.target.warns.create(type = 'truant',
                                                   room = self.room,
                                                   game = self.game)

            self.target.roomstats.filter(room = self.room).update(score = F('score') - 100)



            self.announce()

            



