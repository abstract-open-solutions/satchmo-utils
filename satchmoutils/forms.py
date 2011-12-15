import logging, types
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField

from satchmo_store.contact.models import Contact
from captcha.fields import CaptchaField

from satchmoutils.models import ContactAdministrativeInformation, ContactExtraAddressInformation
from satchmoutils.validators import person_number_validator, buisness_number_validator


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
                
    # handle required
    form.__dict__['clean_person_number'] = types.MethodType(
        clean_person_number,
        form,
        sender
    )
                
def form_extrafield_init_handler(sender, form, **kwargs):
    if 'business_number' not in form.fields:
        form.fields['business_number'] = CharField(
            label = _(u"Business number"),
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
    
    # handle required
    form.__dict__['clean_person_number'] = types.MethodType(
        clean_person_number,
        form,
        sender
    )

def form_extraaddressfield_init_handler(sender, form, **kwargs):
    if 'billing_civicnumber' not in form.fields:
        form.fields['billing_civicnumber'] = CharField(
            label = _(u"Billing Civic number"),
            required = True
        )
    if 'shipping_civicnumber' not in form.fields:
        form.fields['shipping_civicnumber'] = CharField(
            label = _(u"Shipping Civic number"),
            required = True
        )
    if form.data.get('copy_address', False):
        form.fields['shipping_civicnumber'].required = False
    if hasattr(form, '_contact') and \
            isinstance(form._contact, Contact):
        contact = form._contact
        if hasattr(contact, 'contactextraaddressinformation'):
            info = contact.contactextraaddressinformation
            if info.billing_civicnumber:
                form.initial['billing_civicnumber'] = info.billing_civicnumber
            if info.shipping_civicnumber:
                form.initial['shipping_civicnumber'] = info.shipping_civicnumber
                
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
           
def form_extraaddressfield_save_handler(sender, form, **kwargs):
    try:
        data = kwargs['formdata']
        contact = kwargs['object']
    except KeyError, e:
        logging.warning("The form save handler is missing something: %s" % e)
    else:
        billing_civicnumber = data.get('billing_civicnumber', '')
        shipping_civicnumber = data.get('shipping_civicnumber', '')
        if hasattr(contact, 'contactextraaddressinformation'):
           a_info = contact.contactextraaddressinformation
        else:
           a_info = ContactExtraAddressInformation(contact=contact)
        if billing_civicnumber:
           a_info.billing_civicnumber = billing_civicnumber
        if shipping_civicnumber:
           a_info.shipping_civicnumber = shipping_civicnumber
        a_info.save()

def contact_extraaddressfield_view_handler(sender, **kwargs):
    if 'contact' in kwargs and 'contact_dict' in kwargs:
        contact = kwargs['contact']
        contact_dict = kwargs['contact_dict']
        billing_civicnumber = ''
        shipping_civicnumber = ''
        if hasattr(contact, 'contactextraaddressinformation'):
            a_info = contact.contactextraaddressinformation
            billing_civicnumber = a_info.billing_civicnumber
            shipping_civicnumber = a_info.shipping_civicnumber
        contact_dict['eainfo'] = {
            'billing_civicnumber': billing_civicnumber,
            'shipping_civicnumber': shipping_civicnumber,
        }
        
def save_to_model(type_, name, model_, data, form_name = None):
    if form_name is None:
        form_name = name
    fullname = "%s_%s" % (type_, form_name)
    if data.get(fullname, None):
        setattr(model_, name, data[fullname])

def contact_form_postsave(sender, **kwargs):
    logger = logging.getLogger("%s.contact_form_postsave" % __name__)
    try:
        form = kwargs['form']
    except KeyError, e:
        logger.warning("The form save handler is missing something: %s" % e)
    else:
        data = form.cleaned_data
        try:
            contact = form.order.contact
        except:
            contact = form._contact
        
        if not contact:
            return
            
        # BBB: we shopuld check form.changed_data too, here
        for type_ in ['billing', 'shipping']:
            eainfo = getattr(contact, 'contactextraaddressinformation', None)
            if not eainfo:
                eainfo = ContactExtraAddressInformation(
                    contact = contact,
                    billing_civicnumber = ' ',
                    shipping_civicnumber = ' ',
                    )
                eainfo.save()
            form_type = type_
            if type_ == 'shipping' and data.get('copy_address', False):
                form_type = 'billing'
                # Copy "Billing civic number" into "Shipping civic number"
                billing_civicnumber = data.get('billing_civicnumber', False)
                if billing_civicnumber:
                    eainfo.shipping_civicnumber = billing_civicnumber
                    eainfo.save()
