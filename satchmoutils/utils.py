import types
from signals_ahoy.signals import form_init

class ExtraHandler(object):

    signal = None

    @classmethod
    def hook(cls, form_class):
        cls.signal.connect(cls(), sender=form_class)

    def __call__(self, **kwargs):
        pass


class metainitializer(type):

    def __call__(cls, *args, **kwargs):
        dict_ = dict(cls.__dict__.items())
        if len(args) > 0:
            dict_['name'] = args[0]
        if len(args) > 1:
            dict_['instance'] = args[1]
        dict_.update(kwargs)
        return type.__new__(metainitializer, cls.__name__, cls.__bases__, dict_)


class ExtraBase(ExtraHandler):
    __metaclass__ = metainitializer
    signal = form_init


class ExtraField(ExtraBase):

    def __call__(self, **kwargs):
        form = kwargs['form']
        form.fields[self.name] = self.instance


class ExtraMethod(ExtraBase):

    def __call__(self, **kwargs):
        form = kwargs['form']
        form_class = kwargs['sender']
        form.__dict__[self.name] = types.MethodType(
            self.instance,
            form,
            form_class
        )


def add_to_form(form_class, *args):
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, ExtraHandler):
            arg.hook(form_class)
        else:
            raise ValueError("Must be an ExtraHandler class")