from django.conf import settings
settings.configure(DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost', 'PORT': '5432',
        'NAME': 'ggbot',
        'USER': 'ggbot', 'PASSWORD': 'ggbot'
    }
}, TIME_ZONE = 'Asia/Almaty', DEBUG = False)


#settings.configure(DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'HOST': 'localhost', 'PORT': '3306',
#        'NAME': 'gbot_new',
#        'USER': 'gbot_new', 'PASSWORD': 'S3uKuswe'
#    }
#}, TIME_ZONE = 'Asia/Almaty', DEBUG = True)


import os, time
if 'TZ' in os.environ:
    os.environ['TZ'] = 'Asia/Almaty'
    time.tzset()

import locale, platform
locale.setlocale(locale.LC_ALL, 'rus_RUS' if platform.system() == 'Windows' else 'ru_RU.UTF8')

from twisted.python.modules import getModule
for m in getModule('gbot.actions').walkModules(): m.load()

import logging

logging.basicConfig(level = logging.WARN,
        filename = "tmp/log",
        format = "%(asctime)s/%(levelname)s/%(name)s -> %(message)s")

