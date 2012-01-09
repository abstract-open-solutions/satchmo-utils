from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from satchmo_store.shop.models import Cart


def cart_empty(request):
    """
    make empty current cart
    """
    cart = Cart.objects.from_request(request, create=True)
    # make cart empty
    cart.empty()
    return HttpResponseRedirect(reverse('satchmo_cart'))
