import logging, re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField
from captcha.fields import CaptchaField
from payment.forms import PaymentContactInfoForm
from satchmo_store.contact.models import Contact
from satchmo_store.contact.forms import (ExtendedContactInfoForm,
                                         ContactInfoForm)
from satchmoutils.models import ContactAdministrativeInformation
from satchmoutils.validators import (person_number_validator,
                                     # XXX: business
                                     buisness_number_validator)
from satchmoutils.utils import Extender, extends, ExtraField, Fieldset


# XXX: all this should go into settings.py, somewhere, better if in
# SATCHMO_SETTINGS
house_number_countries = ['IT', 'DE']


class ContactForm(forms.Form):
    """The *contact us* form.

    If a user wants to send an inquiry to the site owner, this form allows him
    to do so without making the reserved email address public, which should
    result in less spam.
    """

    sender_fullname = forms.CharField(max_length=100,
                                      required=True)
    company = forms.CharField(max_length=100,
                              required=True)
    city = forms.CharField(max_length=100,
                           required=False)
    telephone = forms.CharField(max_length=100,
                                required=False)
    sender_from_address = forms.EmailField(max_length=100,
                                           required=False)
    message = forms.CharField(widget=forms.widgets.Textarea(),
                              max_length=1000,
                              required=True)
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


class CheckoutFormBaseExtender(Extender):

    @classmethod
    def handle_initdata(cls, **kwargs):
        # pylint: disable=W0212
        form = kwargs['form']
        if hasattr(form, '_contact') and isinstance(form._contact, Contact):
            contact = form._contact
            if hasattr(contact, 'contactadministrativeinformation'):
                info = contact.contactadministrativeinformation
                if info.business_number:
                    form.initial['business_number'] = info.business_number
                if info.person_number:
                    form.initial['person_number'] = info.person_number

    @classmethod
    def handle_postsave(cls, **kwargs):
        data = kwargs['formdata']
        contact = kwargs['object']
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


@extends(ContactInfoForm, ExtendedContactInfoForm)
class ContactExtender(CheckoutFormBaseExtender):
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
        Fieldset(
            'billing',
            _(u'Billing informations'),
            ('person_number',
             'business_number')
        )
    ]


@extends(PaymentContactInfoForm)
class CheckoutExtender(CheckoutFormBaseExtender):
    fields = ContactExtender.fields + [
        ExtraField(
            BooleanField,
            name='commercial_conditions',
            label = _(u"I have read the Terms and Conditions"),
            widget = forms.CheckboxInput(),
            required = True
        )
    ]
    fieldsets = [
        Fieldset(
            'payment',
            _(u'Payment'),
            ('paymentmethod',)
        ),
        Fieldset(
            'personal',
            _(u'Basic informations'),
            ('email',
             'first_name',
             'last_name',
             'phone',
             'organization')
        ),
        Fieldset(
            'billing',
            _(u'Billing informations'),
            ('addressee',
             'street1',
             'city',
             'state',
             'postal_code',
             'country',
             'business_number',
             'person_number')
        ),
        Fieldset(
            'shipping',
            _(u'Shipping informations'),
            ('copy_address',
             'ship_addressee',
             'ship_street1',
             'ship_city',
             'ship_state',
             'ship_postal_code',
             'ship_country')
        )
    ]
