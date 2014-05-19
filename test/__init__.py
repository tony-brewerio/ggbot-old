import os, codecs
import gbot
from django.db import connection, transaction


def scripts(dirname):
    return [open(dirname + '/' + fn).read() for fn in
                sorted(os.listdir(dirname), key = lambda x: int(x.split('_')[0]))]

@transaction.commit_on_success
def setup_package():
    cursor = connection.cursor()
    for sql in scripts('./sql/down') + scripts('./sql/up'): cursor.execute(sql)
    transaction.set_dirty()


@transaction.commit_on_success
def install():
    cursor = connection.cursor()
    for sql in scripts('./sql/up'): cursor.execute(sql)
    cursor.execute("delete from players; delete from rooms;")
    transaction.set_dirty()

