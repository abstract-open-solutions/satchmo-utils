from django.utils.translation import ugettext_lazy as _

from signals_ahoy.signals import form_init, form_postsave
from satchmo_store.contact.signals import satchmo_contact_view
from satchmo_store.contact.forms import ExtendedContactInfoForm, ContactInfoForm

from satchmoutils.forms import form_commercial_conditions_init_handler, \
form_extrafield_init_handler, form_extrafield_save_handler, \
contact_extrafield_view_handler

checkout_std_fields = ('paymentmethod', 'email',  \
'first_name', 'last_name', 'phone',  'organization', 'addressee', 'street1', \
'street2', 'city', 'state', 'postal_code', 'country', 'business_number', \
'person_number', 'copy_address', 'ship_addressee', 'ship_street1', \
'ship_street2', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country')
checkout_payment_fields = (_(u'Payment'), ('paymentmethod',))
checkout_personal_fields = (_(u'Basic informations'), ('email', 'first_name', 'last_name', 'phone',  'organization'))
checkout_billing_fields = (_(u'Billing informations'), ('addressee', 'street1', 'city', 'state', 'postal_code', 'country', 'business_number', 'person_number'))
checkout_shipping_fields = (_(u'Shipping informations'), ('copy_address', 'ship_addressee', 'ship_street1', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country'))
checkout_exclude_fields = ('title', 'next', 'street2', 'ship_street2')

fieldsets = [
    checkout_payment_fields,
    checkout_personal_fields,
    checkout_billing_fields,
    checkout_shipping_fields,
]


# Contact extra fields handler
def form_extrafield_init_handler_wrapper(sender, **kwargs):
    if (sender == ContactInfoForm) or (sender == ExtendedContactInfoForm):
        form_extrafield_init_handler(sender, **kwargs)

form_init.connect(form_extrafield_init_handler_wrapper)

def form_extrafield_save_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if (sender == PaymentContactInfoForm) \
        or (sender == ContactInfoForm) \
        or (sender == ExtendedContactInfoForm):
        form_extrafield_save_handler(sender, **kwargs)

form_postsave.connect(form_extrafield_save_handler_wrapper)

def contact_extrafield_view_handler_wrapper(sender, **kwargs):
    contact_extrafield_view_handler(sender, **kwargs)

satchmo_contact_view.connect(contact_extrafield_view_handler_wrapper)

# Commercial conditions handlers
def form_commercial_conditions_init_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if sender == PaymentContactInfoForm:
        form_commercial_conditions_init_handler(sender, **kwargs)

form_init.connect(form_commercial_conditions_init_handler_wrapper)

# Grouping fields for checkout form refactoring
def form_group_fields_init_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if sender == PaymentContactInfoForm:
        form = kwargs['form']
        checkout_fields = dict([(f.name, f) for f in form])
        checkout_fields_ids = tuple(checkout_fields.keys())
        form.fieldsets = []
        used_fields = []
        for fieldset in fieldsets:
            fieldset_fields = []
            for f in fieldset[1]:
                if f in checkout_shipping_fields[1] and f != 'copy_address':
                    class_ = 'shiprow'
                else:
                    class_ = ''
                used_fields.append(f)
                fieldset_fields.append(
                    {
                        'id':checkout_fields[f].auto_id, 
                        'field':checkout_fields[f],
                        'class':class_
                    }
                )
            form.fieldsets.append(
                {
                    'title': fieldset[0], 
                    'fields': fieldset_fields
                }
            )
        
        # Additional fields
        other_fields_ids = list(set(checkout_fields_ids) - set(checkout_std_fields))
        other_fields = []
        for fid in other_fields_ids:
            if fid not in checkout_exclude_fields:
                other_fields.append({'id':checkout_fields[fid].auto_id, 'field':checkout_fields[fid]})
                
        if other_fields:
            form.fieldsets.append(
                {
                    'title': _(u'Other fields'), 
                    'fields': other_fields
                }
            )

form_init.connect(form_group_fields_init_handler_wrapper)
