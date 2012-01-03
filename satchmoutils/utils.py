import types
import abc

from django.utils.translation import ugettext_lazy as _


class AbstractDynamicForm(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def set_data(self):
        """
        This is an abstract method.
        Should have implemented this method to set 
        additional fields into the form.
        """
        raise NotImplementedError("Should have implemented this")
    
    @abc.abstractmethod
    def save_data(self, **kwargs):
        """
        This is an abstract method.
        Should have implemented this method to save additional data 
        dynamically injected into the form.
        """
        raise NotImplementedError("Should have implemented this")
    
class DynamicForm(object):
    """
    Dynamic form that allows the user to change 
    and then verify the data that was parsed
    """

    def __init__(self, form=None):
        self.form = form

    def add_fields(self, fields=()):
        """ Add multiple fields to the given form """
        for field in fields:
            self.add_field(**field)
                
    def add_field(self, field_name=None, field_label='', field_class=None, 
                    validators=[], required=False, fieldset='', widget=None, choices=[]):
        """ Add single field to the given form """
        args = {
            'label' : _(u"%s" % field_label),
            'validators' : validators,
            'required' : required,
            'widget' : widget
        }
        if choices:
            args['choices'] = choices
            
        if field_name not in self.form.fields:
            self.form.fields[field_name] = field_class(**args)

    def add_methods(self, sender, methods=()):
        """ Add multiple methods to the given form """
        for key, method in methods:
            self.add_method(sender, key, method)

    def add_method(self, sender, key, method):
        """ Add single method to the given form """
        self.form.__dict__[key] = types.MethodType(
            method,
            self.form,
            sender
        )
    
    def set_data(self):
        """ To implements """
        return

    def save_data(self, **kwargs):
        """ To implements """
        return

AbstractDynamicForm.register(DynamicForm)
