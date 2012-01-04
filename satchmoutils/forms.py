import logging, re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField
from satchmo_store.contact.forms import (ExtendedContactInfoForm, 
            ContactInfoForm)
from payment.forms import PaymentContactInfoForm

from satchmo_store.contact.models import Contact
from captcha.fields import CaptchaField

from satchmoutils.models import ContactAdministrativeInformation
from satchmoutils.validators import (person_number_validator, 
            buisness_number_validator)

from satchmoutils.utils import Extender, extends, ExtraField, Fieldset

house_number_countries = ['IT', 'DE']
checkout_std_fields = ('paymentmethod', 'email', \
'first_name', 'last_name', 'phone', 'organization', 'addressee', 'street1', \
'street2', 'city', 'state', 'postal_code', 'country', 'business_number', \
'person_number', 'copy_address', 'ship_addressee', 'ship_street1', \
'ship_street2', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country')
checkout_exclude_fields = ('title', 'next', 'street2', 'ship_street2')

sorted_fieldsets_keys = ['payment', 'personal', 'billing', 'shipping']


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

# Dynamic customizing checkout form
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
    # BBB: what are the countries that use the house number?
    regex = re.compile(r"\w+-?\s?([^\d]\w)*\s?(\d+)")
    check = regex.match(address)
    if country in house_number_countries:
        if not check:
            raise ValidationError(
                message = _(
                    u"You must specify house number"
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
    copy_address = self.cleaned_data.get('copy_address', False)
    if copy_address:
        shipping_address = self.cleaned_data.get('street1', '')
    return address_validator(shipping_country, shipping_address)

class BaseExtender(Extender):

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

    def address_validator(self, country, address):
        # BBB: what are the countries that use the house number?
        regex = re.compile(r"\w+-?\s?([^\d]\w)*\s?(\d+)")
        check = regex.match(address)
        if country in house_number_countries:
            if not check:
                raise ValidationError(
                    message = _(
                        u"You must specify house number"
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
        return self.address_validator(billing_country, billing_address)

    def clean_ship_street1(self):
        shipping_address = self.cleaned_data.get('ship_street1', '')
        shipping_country = self.cleaned_data.get('ship_country', 'IT')
        copy_address = self.cleaned_data.get('copy_address', False)
        if copy_address:
            shipping_address = self.cleaned_data.get('street1', '')
        return self.address_validator(shipping_country, shipping_address)
        
    @classmethod
    def handle_initdata(cls, **kwargs):
        form = kwargs.get('form', None)
        if form and hasattr(form, '_contact') and \
                isinstance(form._contact, Contact):
            contact = form._contact
            if hasattr(contact, 'contactadministrativeinformation'):
                info = contact.contactadministrativeinformation
                if info.business_number:
                    form.initial['business_number'] = info.business_number
                if info.person_number:
                    form.initial['person_number'] = info.person_number
                    
    @classmethod
    def handle_postsave(cls, **kwargs):
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
            
@extends(PaymentContactInfoForm)
class CheckoutExtender(BaseExtender):
    fields = [
        ExtraField(CharField, name='business_number',
            label = 'Vat number',
            validators = [buisness_number_validator,],
            required = False,
        ),
        ExtraField(CharField, name='person_number',
            label = 'Person number',
            validators = [person_number_validator,],
            required = False,
        ),
        ExtraField(BooleanField, name='commercial_conditions',
            label = 'I have read the Terms and Conditions.',
            widget = forms.CheckboxInput(),
            required = True,
        )
    ]
    fieldsets = [
        Fieldset('payment', _(u'Payment'), 'paymentmethod',),
        Fieldset('personal', _(u'Basic informations'), ('email', 'first_name', \
                        'last_name', 'phone', 'organization')),
        Fieldset('billing', _(u'Billing informations'), ('addressee', 'street1', \
                        'city', 'state', 'postal_code', 'country', 'business_number', \
                        'person_number')),
        Fieldset('shipping', _(u'Shipping informations'), ('copy_address', \
                        'ship_addressee', 'ship_street1', 'ship_city', 'ship_state', \
                        'ship_postal_code', 'ship_country')),
    ]
    
@extends(ContactInfoForm, ExtendedContactInfoForm)
class ContactExtender(BaseExtender):
    fields = [
        ExtraField(CharField, name='business_number',
            label = 'Vat number',
            validators = [buisness_number_validator,],
            required = False,
        ),
        ExtraField(CharField, name='person_number',
            label = 'Person number',
            validators = [person_number_validator,],
            required = False,
        )
    ]
    fieldsets = [
        Fieldset('billing', _(u'Billing informations'), 
            ('person_number', 'business_number')),
    ]
