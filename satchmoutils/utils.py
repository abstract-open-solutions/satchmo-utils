import types
from django.utils.translation import ugettext_lazy as _


class DynForm(object):
    """
    Dynamic form that allows the user to change 
    and then verify the data that was parsed
    """

    def __init__(self, form=None):
        self.form = form

    def add_field(self, field_name, field_label, field_class, 
                    validators, required, fieldset, widget):
        if field_name not in self.form.fields:
            self.form.fields[field_name] = field_class(
                label = _(u"%s" % field_label),
                validators = validators,
                required = required,
                widget=widget
            )
            
    def add_method(self, sender, key, method):
        self.form.__dict__[key] = types.MethodType(
            method,
            self.form,
            sender
        )

    def set_data(self):
        """
        Set the data to include in the form
        """
        raise NotImplemented
        
    def save_data(self, **kwargs):
        """
        Save the data to include in the form
        """
        raise NotImplemented
