from signals_ahoy.signals import form_init, form_postsave
from django.db.models.signals import post_save
from satchmo_store.contact.signals import satchmo_contact_view
from satchmo_store.shop.models import Order
from satchmo_store.contact.forms import ExtendedContactInfoForm, ContactInfoForm

from satchmoutils.forms import form_commercial_conditions_init_handler, form_extrafield_init_handler, \
form_extraaddressfield_init_handler, form_extrafield_save_handler, contact_extrafield_view_handler, \
form_extraaddressfield_save_handler, contact_extraaddressfield_view_handler, contact_form_postsave


# Shop evaluation handlers
def form_shop_evaluation_init_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    if sender == PaymentContactInfoForm:
        form_shop_evaluation_init_handler(sender, **kwargs)

form_init.connect(form_shop_evaluation_init_handler_wrapper)

def form_shop_evaluation_save_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    if sender == PaymentContactInfoForm:
        form_shop_evaluation_save_handler(sender, **kwargs)

form_postsave.connect(form_shop_evaluation_save_handler_wrapper)

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

# Extra address fields handlers
def form_extraaddressfield_init_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if (sender == PaymentContactInfoForm) \
        or (sender == ContactInfoForm) \
        or (sender == ExtendedContactInfoForm):
        form_extraaddressfield_init_handler(sender, **kwargs)

form_init.connect(form_extraaddressfield_init_handler_wrapper)


def form_extraaddressfield_save_handler_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if (sender == PaymentContactInfoForm) \
        or (sender == ContactInfoForm) \
        or (sender == ExtendedContactInfoForm):
        form_extraaddressfield_save_handler(sender, **kwargs)

form_postsave.connect(form_extraaddressfield_save_handler_wrapper)


def contact_extraaddressfield_view_handler_wrapper(sender, **kwargs):
    contact_extraaddressfield_view_handler(sender, **kwargs)

satchmo_contact_view.connect(contact_extraaddressfield_view_handler_wrapper)

# Contact post-save handler
def contact_form_postsave_wrapper(sender, **kwargs):
    from payment.forms import PaymentContactInfoForm
    
    if (sender == PaymentContactInfoForm) \
        or (sender == ContactInfoForm) \
        or (sender == ExtendedContactInfoForm):
        contact_form_postsave(sender, **kwargs)

form_postsave.connect(contact_form_postsave_wrapper)

# Order update full ship/bill addresses
def updateAddressesInOrder(sender, **kwargs):
    """
    devo far convergere anche i numeri civici negli indirizzi di fatturazione/consegna
    """
    order = kwargs['instance']
    billing_civicnumber = shipping_civicnumber = ''
    try:
        billing_civicnumber = order.contact.contactextraaddressinformation.billing_civicnumber
        shipping_civicnumber = order.contact.contactextraaddressinformation.shipping_civicnumber
    except:
        pass

    if billing_civicnumber and (billing_civicnumber not in order.bill_street1):
        bill_street_full = "%s %s" % (order.bill_street1, billing_civicnumber)
        order.bill_street1 = bill_street_full
    
    if shipping_civicnumber and (shipping_civicnumber not in order.ship_street1):
        ship_street_full = "%s %s" % (order.ship_street1, shipping_civicnumber)
        order.ship_street1 = ship_street_full

post_save.connect(updateAddressesInOrder, sender=Order)