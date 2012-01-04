from signals_ahoy.signals import form_init, form_initdata, form_postsave


class ExtraField(object):

    def __init__(self, klass, name, **kwargs):
        self.name = name
        self.klass = klass
        self.kwargs = kwargs

    def __call__(self):
        return self.klass(**self.kwargs)


class Fieldset(object):

    def __init__(self, id_, label, *fields):
        self.id_ = id_
        self.label = label
        self.fields = fields
        self.form = None

    def bind(self, form):
        copy = self.__class__(self.id_, self.label, *self.fields)
        copy.form = form
        return copy


def extends(*form_classes):
    def wrapper(extender):
        for form_class in form_classes:
            form_init.connect(extender.handle_init, sender=form_class)
            if hasattr(extender, 'handle_initdata'):
                form_initdata.connect(extender.handle_initdata,
                                      sender=form_class)
            if hasattr(extender, 'handle_postsave'):
                form_postsave.connect(extender.handle_postsave,
                                      sender=form_class)
        return extender
    return wrapper


class Extender(object):
    """Usage

        >>> @extends(MyForm)
        >>> class MyExtender(Extender):
        ...     fields = [
        ...         ExtraField(CharField, name='foo')
        ...     ]
        ...     fieldsets = [
        ...         Fieldset('test', _(u"Test"), 'foo')
        ...     ]
        ...     @classmethod
        ...     def handle_initdata(cls, **kwargs):
        ...         pass
        ...     @classmethod
        ...     def handle_postsave(cls, **kwargs):
        ...         pass
    """

    @classmethod
    def handle_init(cls, **kwargs):
        form = kwargs['form']
        for extrafield in cls.fields:
            form.fields[extrafield.name] = extrafield()
        if hasattr(cls, 'fieldsets') and len(cls.fieldsets) > 0:
            if not hasattr(form, 'fieldsets'):
                form.fieldsets = []
            form.fieldsets.extend([ f.bind(form) for f in cls.fieldsets ])
