from types import MethodType
from collections import Sequence
from signals_ahoy.signals import form_init, form_postsave


class ExtraField(object):

    def __init__(self, klass, name, **kwargs):
        self.name = name
        self.klass = klass
        self.kwargs = kwargs

    def __call__(self):
        return self.klass(**self.kwargs)


class Fieldset(object):

    def __init__(self, id_, label, fields, before=None):
        self.id_ = id_
        self.label = label
        self.fields = fields
        self.before = before
        self.form = None
        self._reorder()

    def _reorder(self):
        new_fields = []
        for field in self.fields:
            if isinstance(field, tuple):
                try:
                    index = self.fields.index(field[1])
                except ValueError:
                    new_fields.append(field[0])
                else:
                    new_fields.insert(index, field[0])
            else:
                new_fields.append(field)
        self.fields = new_fields

    def bind(self, form):
        copy = self.__class__(self.id_, self.label, self.fields,
                              before=self.before)
        copy.form = form
        return copy

    def merge(self, other):
        self.label = other.label
        self.fields.extend(other.fields)
        if other.before:
            self.before = other.before
        self._reorder()

    def items(self):
        for field_name in self.fields:
            yield (field_name, self.form[field_name])


class Fieldsets(Sequence):

    def __init__(self, initial = tuple()):
        self.elements = list(initial)
        self.ids = {}
        for element in self.elements:
            self.ids[element.id_] = element

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, item):
        return item.id_ in self.ids

    def __getitem__(self, index):
        return self.elements[index]

    def _reorder(self):
        for index, element in enumerate([ e for e in self.elements ]):
            if element.before is not None:
                try:
                    new_index = self.elements.index(self.ids[element.before])
                except (KeyError, ValueError):
                    pass
                else:
                    del self.elements[index]
                    self.elements.insert(new_index, element)

    def add(self, item):
        if item.id_ in self.ids:
            fieldset = self.ids[item.id_]
            fieldset.merge(item)
        else:
            self.ids[item.id_] = item
            self.elements.append(item)
        self._reorder()

    def update(self, items):
        for item in items:
            self.add(item)


def extends(*form_classes):
    def wrapper(extender):
        for form_class in form_classes:
            form_init.connect(extender.handle_init, sender=form_class)
            if hasattr(extender, 'handle_initdata'):
                form_init.connect(extender.handle_initdata,
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

    fields = []
    methods = {}

    @classmethod
    def handle_init(cls, **kwargs):
        form = kwargs['form']
        for extrafield in cls.fields:
            form.fields[extrafield.name] = extrafield()
        for name, method in cls.methods.items():
            form.__dict__[name] = MethodType(method, form,
                                                   form.__class__)
        if hasattr(cls, 'fieldsets') and len(cls.fieldsets) > 0:
            if not hasattr(form, 'fieldsets'):
                form.fieldsets = Fieldsets()
            form.fieldsets.update([ f.bind(form) for f in cls.fieldsets ])
