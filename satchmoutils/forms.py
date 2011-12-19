import logging, types, re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField

from satchmo_store.contact.models import Contact
from captcha.fields import CaptchaField

from satchmoutils.models import ContactAdministrativeInformation
from satchmoutils.validators import person_number_validator, \
buisness_number_validator

civic_number_countries = ['IT', 'DE']


# "Contact Us" Form
class ContactForm(forms.Form):
    sender_fullname = forms.CharField(required=True, max_length=100)
    company = forms.CharField(required=False, max_length=100)
    city = forms.CharField(required=False, max_length=100)
    telephone = forms.CharField(required=False, max_length=100)
    sender_from_address = forms.EmailField(required=True, max_length=100)
    message = forms.CharField(required=True, 
        widget=forms.widgets.Textarea(), 
        max_length=1000)
    captcha = CaptchaField(required=True)
    
def clean_person_number(self):
    business_number = self.cleaned_data.get('business_number', None)
    person_number = self.cleaned_data.get('person_number', None)
    if business_number or person_number:
        return person_number
    else:
        raise ValidationError(
            message = _(
                u"You must specify either your person number or the VAT number"
                u" of your company in order to proceed with the purchase"
            ),
            code = 'invalid'
        )

def address_validator(country, address):
    regex = re.compile(r"\w+-?\s?([^\d]\w)*\s?(\d+)")
    check = regex.match(address)
    if country in civic_number_countries:
        if not check:
            raise ValidationError(
                message = _(
                    u"You must specify civic number"
                    u" in your address"
                ),
                code = 'invalid'
            )
        else:
            return address
    else:
        return address

def clean_street1(self):
    billing_address = self.cleaned_data.get('street1', '')
    billing_country = self.cleaned_data.get('country', 'IT')
    return address_validator(billing_country, billing_address)

def clean_ship_street1(self):
    shipping_address = self.cleaned_data.get('ship_street1', '')
    shipping_country = self.cleaned_data.get('ship_country', 'IT')
    return address_validator(shipping_country, shipping_address)
    
clean_methods = (
    ('clean_person_number', clean_person_number),
    ('clean_street1', clean_street1),
    ('clean_ship_street1', clean_ship_street1)
)

def form_commercial_conditions_init_handler(sender, form, **kwargs):
    if 'business_number' not in form.fields:
        form.fields['business_number'] = CharField(
            label = _(u"Vat number"),
            validators = [buisness_number_validator,],
            required = False
        )
    if 'person_number' not in form.fields:
        form.fields['person_number'] = CharField(
            label = _(u"Person number"),
            validators = [person_number_validator,],
            required = False
        )
    if 'commercial_conditions' not in form.fields:
        form.fields['commercial_conditions'] = BooleanField(
            label = _(u"I have read the Terms and Conditions."),
            required = True,
            widget=forms.CheckboxInput()
        )
    if hasattr(form, '_contact') and \
            isinstance(form._contact, Contact):
        contact = form._contact
        if hasattr(contact, 'contactadministrativeinformation'):
            info = contact.contactadministrativeinformation
            if info.business_number:
                form.initial['business_number'] = info.business_number
            if info.person_number:
                form.initial['person_number'] = info.person_number
    
    # custom clean methods
    for key, method in clean_methods:
        form.__dict__[key] = types.MethodType(
            method,
            form,
            sender
        )
                
def form_extrafield_init_handler(sender, form, **kwargs):
    if 'business_number' not in form.fields:
        form.fields['business_number'] = CharField(
            label = _(u"VAT number"),
            validators = [buisness_number_validator,],
            required = False
        )
    if 'person_number' not in form.fields:
        form.fields['person_number'] = CharField(
            label = _(u"Person number"),
            validators = [person_number_validator,],
            required = False
        )
    if hasattr(form, '_contact') and \
            isinstance(form._contact, Contact):
        contact = form._contact
        if hasattr(contact, 'contactadministrativeinformation'):
            info = contact.contactadministrativeinformation
            if info.business_number:
                form.initial['business_number'] = info.business_number
            if info.person_number:
                form.initial['person_number'] = info.person_number
    
    # custom clean methods
    for key, method in clean_methods:
        form.__dict__[key] = types.MethodType(
            method,
            form,
            sender
        )

def form_extrafield_save_handler(sender, form, **kwargs):
    try:
        data = kwargs['formdata']
        contact = kwargs['object']
    except KeyError, e:
        logging.warning("The form save handler is missing something: %s" % e)
    else:
        business_number = data.get('business_number', '')
        person_number = data.get('person_number', '')
        if hasattr(contact, 'contactadministrativeinformation'):
           a_info = contact.contactadministrativeinformation
        else:
           a_info = ContactAdministrativeInformation(contact=contact)
        if business_number:
           a_info.business_number = business_number
        if person_number:
           a_info.person_number = person_number
        a_info.save()

def contact_extrafield_view_handler(sender, **kwargs):
    if 'contact' in kwargs and 'contact_dict' in kwargs:
        contact = kwargs['contact']
        contact_dict = kwargs['contact_dict']
        if hasattr(contact, 'contactadministrativeinformation'):
           a_info = contact.contactadministrativeinformation
           contact_dict['adminfo'] = {
               'business_number': a_info.business_number,
               'person_number': a_info.person_number,
           }
