from signals_ahoy.signals import form_init, form_postsave
from satchmo_store.contact.signals import satchmo_contact_view
from satchmo_store.contact.forms import ExtendedContactInfoForm, ContactInfoForm

from satchmoutils.forms import form_commercial_conditions_init_handler, \
form_extrafield_init_handler, form_extrafield_save_handler, \
contact_extrafield_view_handler


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
