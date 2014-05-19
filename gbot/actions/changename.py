from gbot.action import Action
from gbot import param

class ChangeName(Action):

#    expose = '!changename',
    groups = 'admin',

    params = ['old_player', param.Player(),
              'new_player', param.Player()]

    def action(self):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute("select merge_players(%s, %s);",
                       [self.old_player.id, self.new_player.id])
        transaction.set_dirty()

        self.announce()
