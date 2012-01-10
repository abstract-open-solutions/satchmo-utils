#!/usr/bin/env python
import logging

from django.http import HttpResponseRedirect
from django.core import urlresolvers

from satchmo_store.shop.models import Cart

log = logging.getLogger('primifrutti.ui.views')


# Make Emty Cart View
def cart_empty(request):
    """
    make empty current cart
    """
    cart = Cart.objects.from_request(request, create=True)
    
    # make cart empty
    cart.empty()
    return HttpResponseRedirect(urlresolvers.reverse('satchmo_cart'))
    