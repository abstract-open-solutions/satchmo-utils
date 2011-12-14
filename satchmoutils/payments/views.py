from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from satchmo_utils.views import bad_or_missing
from satchmo_store.shop.models import Order

from livesettings import config_value
from product.models import Discount
from satchmo_store.mail import NoRecipientsException, send_store_mail, send_store_mail_template_decorator
from satchmo_store.shop.signals import order_confirmation_sender, order_notice_sender

import logging

log = logging.getLogger('contact.notifications')

def order_suspend_listener(order=None, **kwargs):
    """Listen for order_suspend signal, and send confirmations"""
    if order:
        send_order_suspend(order)
        send_order_notice_suspend(order)

@send_store_mail_template_decorator('shop/email/order_suspend')
def send_order_suspend(order, template='', template_html=''):
    """Send an order suspend mail to the customer.
    """

    try:
        sale = Discount.objects.by_code(order.discount_code, raises=True)
    except Discount.DoesNotExist:
        sale = None
    
    c = {'order': order, 'sale' : sale}
    subject = _("%(shop_name)s : Your order was suspended")
    
    send_store_mail(subject, c, template, [order.contact.email],
                    template_html=template_html, format_subject=True,
                    sender=order_confirmation_sender)

@send_store_mail_template_decorator('shop/email/order_suspend_notice')
def send_order_notice_suspend(order, template='', template_html=''):
    """Send an order suspend mail to the owner.
    """

    if config_value("PAYMENT", "ORDER_EMAIL_OWNER"):
        try:
            sale = Discount.objects.by_code(order.discount_code, raises=True)
        except Discount.DoesNotExist:
            sale = None

        c = {'order': order, 'sale' : sale}
        subject = _("%(shop_name)s : Suspended order")

        eddresses = []
        more = config_value("PAYMENT", "ORDER_EMAIL_EXTRA")
        if more:
            eddresses = set([m.strip() for m in more.split(',')])
            eddresses = [e for e in eddresses if e]

        try:
            send_store_mail(subject, c, template, eddresses,
                            template_html=template_html, format_subject=True,
                            send_to_store=True, sender=order_notice_sender)
        except NoRecipientsException:
            log.warn("No shop owner email specified, skipping owner_email")
            return


def suspended(request):
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

    del request.session['orderID']
    return render_to_response('shop/checkout/suspended.html',
                              {'order': order},
                              context_instance=RequestContext(request))


suspended = never_cache(suspended)
