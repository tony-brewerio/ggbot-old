import logging
from django.db import transaction
from twisted.internet.task import LoopingCall
from gbot.exceptions import BotError
from gbot.templates import render_lines
from gbot.util import split_by
from gbot.models import Membership
from time import time
from django import db


url_map = dict()


class ActionMeta(type):

    def __init__(self, name, bases, attrs):
        type.__init__(self, name, bases, attrs)

        self.action = transaction.commit_on_success(self.action)

        for url in self.expose:
            url_map[url] = self


class Action(object):
    __metaclass__ = ActionMeta

    msgbox_only = False

    expose = []
    params = []
    groups = []

    def __str__(self):
        return "A[%s:%s:%s]" % (self.__class__.__name__,
                                getattr(self, 'bot', '?'),
                                getattr(self, 'player', '?'))

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.log = logging.getLogger(str(self))
        self.log.debug(u"initialize")
        self.groups = self.__class__.groups

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.clear_output()
        self.log.debug(u"running with params_string => %s",
                       getattr(self, 'param_string', None))

        try:
            try:
                moment = time()
                self.deny_by_msgbox()
                self.deny_by_membership()
                self.parse_param_string()
                self.__dict__.update(self.action() or {})

#                self.log.warn(u"ran in %sms", 1000 * (time() - moment))
#
#                for sql in db.connection.queries:
#                    if float(sql['time']) >= 0.01:
#                        self.log.warn(u"sql (time:%s) => %s", sql['time'], sql['sql'])

                db.reset_queries()

            except BotError, bot_error:
                self.clear_output()
                self.log.debug(u"BotError(%s) => %s", bot_error.template_name, bot_error.kwargs)
                self.private(bot_error.template_name, **bot_error.kwargs)

        except Exception, e:
            self.clear_output()
            self.private('system/system_error')
            self.log.exception(e)

        return self

    def clear_output(self):
        self.announces, self.privates, self.kicks = [], [], []

    def deny_by_msgbox(self):
        if self.msgbox_only and not self.reply_to_msgbox:
            raise BotError('system/deny_by_msgbox')

    def deny_by_membership(self):
        room = getattr(self, 'room', None)
        player = getattr(self, 'player', None)
        if room and player and self.groups and not player.member_of(room, *self.groups):
            raise BotError('system/deny_by_membership')

    def parse_param_string(self):
        param_string = getattr(self, 'param_string', '')
        raw_params = filter(None, param_string.split(None, ((len(self.params) or 2) / 2) - 1))
        for name, parser in zip(self.params[::2], self.params[1::2]):
            setattr(self, name, parser(self, raw_params.pop(0) if raw_params else None))


    def render_lines(self, *args, **kwargs):
        action_name = self.__class__.__name__.lower()
        template_name = args[0] if args else action_name
        template = ('ru/%s/%s' % (action_name, template_name)) if not '/' in template_name else 'ru/' + template_name
        return render_lines(template, **dict(self.__dict__, **kwargs))

    def announce(self, *args, **kwargs):
        self.announces.extend(self.render_lines(*args, line_length = 480, **kwargs))

    def private(self, *args, **kwargs):
        send_to = kwargs.get('to', getattr(self, 'player', None))
        self.privates.extend((send_to, l)
            for l in self.render_lines(*args, line_length = 148, **kwargs))

    def kick(self, target, reason):
        self.kicks.append((target, reason))



    def action(self): pass


class JobMeta(ActionMeta):

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)

        cls.action = transaction.commit_on_success(cls.action)
        cls.log = logging.getLogger('[J:%s]' % cls.__name__)

        interval = getattr(cls, 'interval')
        if interval:
            cls.looping_call = LoopingCall(cls.execute)
            cls.looping_call.start(interval, now=False)


class Job(Action):
    __metaclass__ = JobMeta

    reply_to_msgbox = False

    log = logging.getLogger('[J]')

    interval = None
    bots = []

    @classmethod
    def execute(cls):
        from gbot.bot import Bot
        for bot_name in cls.bots:
            bot = Bot.bot_by_name.get(bot_name)
            if bot:
                try:
                    cls.execute_bot(bot)
                except BaseException:
                    cls.log.exception(u'Job execution failure')
                    pass

    @classmethod
    def execute_bot(cls, bot):
        action = cls(room=bot.room, bot=bot)()

        for announce in action.announces:
            bot.announces.put(announce)

        for target, message in action.privates:
            bot.log.info(u"PVT @ %s -> %s", target, message)
            bot.privates.put((target.id, message))

        for target, reason in action.kicks:
            bot.kicks.put((target.id, reason))

























