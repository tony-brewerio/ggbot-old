
class BotError(Exception):

    def __init__(self, template_name, **kwargs):
        self.kwargs = kwargs
        self.template_name = template_name
        self.__dict__.update(kwargs)