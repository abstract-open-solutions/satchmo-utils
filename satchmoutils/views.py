#!/usr/bin/env python
import logging

from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from satchmo_store.shop.models import Config
from satchmo_store.shop.models import Cart

from satchmoutils.forms import ContactForm

try:
    from django.utils import simplejson
except ImportError:
    import simplejson
    
log = logging.getLogger('primifrutti.ui.views')

time_format = "%d-%m-%Y %H:%M:%S"

error_msg = u"ERROR. Some fields do contain wrong values. Please correct the errors below"


# Contacts View
def get_form(request):
    return_message = ''
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return_message = contacts_action(form)
        else:
            return_message = _(error_msg)
    else:
        form = ContactForm()
    return form, return_message


@never_cache
def contacts(request):
    """Contact form
    """
    form, return_message = get_form(request)
    
    context = RequestContext(request, {
        'form': form,
        'message': return_message
    })
    return render_to_response(
        "shop/contacts.html",
        context_instance=context
    )


def contacts_action(form):
    """Execute the contact us action.
    Sends an email to the addres taken from settings.
    """

    sender_fullname = form.cleaned_data['sender_fullname']
    sender_from_address = form.cleaned_data['sender_from_address']
    company = form.cleaned_data['company']
    city = form.cleaned_data['city']
    telephone = form.cleaned_data['telephone']
    message = form.cleaned_data['message']

    # Send email
    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    to_address = True and shop_email or settings.EMAIL_NOTIFICATION
    subject = "InfoFarm"
    mail_message = """
    %(full_name)s
    %(email)s
    %(company)s
    %(city)s
    %(telephone)s

    %(message)s
    """ % {
    'full_name' : sender_fullname,
    'email' : sender_from_address,
    'company' : company,
    'city' : city,
    'telephone' : telephone,
    'message' : message,
    }
    try:
        send_mail(subject, mail_message, sender_from_address, [to_address,])
        contact_msg = _(u"Message sent.")
    except:
        contact_msg = _(error_msg)
    return contact_msg


# Make Emty Cart View
def cart_empty(request):
    """
    make empty current cart
    """
    cart = Cart.objects.from_request(request, create=True)
    
    # make cart empty
    cart.empty()
    return HttpResponseRedirect(urlresolvers.reverse('satchmo_cart'))
    