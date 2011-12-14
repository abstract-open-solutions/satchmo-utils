#!/usr/bin/env python
import logging
from ajax_select import get_lookup
from decimal import Decimal

from django.db.models import Q
from django.contrib.sites.models import Site
from django.core.xheaders import populate_xheaders
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import check_for_language
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.decorators.cache import cache_control #products_number
from django.utils.translation import ugettext
from django.contrib.auth.decorators import login_required
from livesettings import config_value

from satchmo_store.shop.exceptions import CartAddProhibited
from satchmo_store.shop.models import Cart
from satchmo_store.shop.signals import satchmo_cart_changed, satchmo_cart_add_complete, satchmo_cart_details_query
from satchmo_utils.numbers import RoundedDecimalError, round_decimal
from satchmo_utils.views import bad_or_missing
from satchmo_store.shop.models import Config
from satchmo_store.shop.views.orders import order_history
from satchmo_store.shop.views.cart import decimal_too_big, _product_error, product_from_post, _json_response
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Order
from satchmo_store.shop.signals import cart_add_view
from satchmo_store.contact.views import AjaxGetStateException, ContactInfoForm, area_choices_for_country
from product.models import Product, Category
from product.utils import find_best_auto_discount
from product.views import find_product_template

from primifrutti.ui.forms import ContactForm
from primifrutti.product.models import PrimifruttiProduct

try:
    from django.utils import simplejson
except ImportError:
    import simplejson
    
log = logging.getLogger('primifrutti.ui.views')

time_format = "%d-%m-%Y %H:%M:%S"


def classview(cls):
    def view_wrapper(request, *args, **kwargs):
        instance = cls(request, *args, **kwargs)
        return instance()
    return view_wrapper


# Contacts View
def get_form(request):
    return_message = ''
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return_message = contacts_action(form)
        else:
            return_message = "ERRORE! Per favore, controlla le informazioni inserite"
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
        contact_msg = _(u"Messaggio spedito!")
    except:
        contact_msg = _(u"ERRORE! Per favore, controlla le informazioni inserite")
        
    return contact_msg
    
    
def smart_add(request):
    """Redirect the request to cart_add (infofarma) or whatever gets returned by
    the cart_add_view signal."""
    
    method={'view': cart_add}
    cart_add_view.send(Cart, request=request, method=method)
    
    return method['view'](request)
    
def cart_add(request, id=0, redirect_to='satchmo_cart'):
    """Add an item to the cart."""
    log.debug('FORM: %s', request.POST)
    formdata = request.POST.copy()
    productslug = None

    cartplaces = config_value('SHOP', 'CART_PRECISION')
    roundfactor = config_value('SHOP', 'CART_ROUNDING')

    if formdata.has_key('productname'):
        productslug = formdata['productname']
    try:
        product, details = product_from_post(productslug, formdata)

        if not (product and product.active and product.unit_price):
            log.debug("product %s is not active" % productslug)
            return bad_or_missing(request, _("That product is not available at the moment."))
        else:
            log.debug("product %s is active" % productslug)
            
    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.debug("Could not find product: %s", productslug)
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    # First we validate that the number isn't too big.
    if decimal_too_big(formdata['quantity']):
        return _product_error(request, product, _("Please enter a smaller number."))

    # Then we validate that we can round it appropriately.
    try:
        quantity = round_decimal(formdata['quantity'], places=cartplaces, roundfactor=roundfactor)
    except RoundedDecimalError, P:
        return _product_error(request, product,
            _("Invalid quantity."))

    if quantity <= Decimal('0'):
        return _product_error(request, product,
            _("Please enter a positive number."))

    cart = Cart.objects.from_request(request, create=True)
    # send a signal so that listeners can update product details before we add it to the cart.
    satchmo_cart_details_query.send(
            cart,
            product=product,
            quantity=quantity,
            details=details,
            request=request,
            form=formdata
            )
    try:
        added_item = cart.add_item(product, number_added=quantity, details=details)

    except CartAddProhibited, cap:
        return _product_error(request, product, cap.message)

    # got to here with no error, now send a signal so that listeners can also operate on this form.
    satchmo_cart_add_complete.send(cart, cart=cart, cartitem=added_item, product=product, request=request, form=formdata)
    satchmo_cart_changed.send(cart, cart=cart, request=request)

    if request.is_ajax():
        data = {}
        data['id'] = product.id
        data['name'] = product.translated_name()
        data['cart_count'] = str(round_decimal(cart.numItems, 2))
        data['cart_total'] = str(cart.total)
        # Legacy result, for now
        data['results'] = _("Success")
        log.debug('CART AJAX: %s', data)
        
        return _json_response(data)
    else:
        url = urlresolvers.reverse(redirect_to)
        return HttpResponseRedirect(url)
        
@never_cache
def display_cart(request, cart=None, error_message='', default_view_tax=None):
    """Display the items in the cart."""
    if default_view_tax is None:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if not cart:
        cart = Cart.objects.from_request(request)

    if cart.numItems > 0:
        products = [item.product for item in cart.cartitem_set.all()]
        sale = find_best_auto_discount(products)
    else:
        sale = ''

    context = RequestContext(request, {
        'cart': cart,
        'error_message': error_message,
        'default_view_tax' : default_view_tax,
        'sale_cart' : sale,
        })
    return render_to_response('shop/cart.html', context_instance=context)

# Make Emty Cart View
def cart_empty(request):
    """
    make empty current cart
    """
    cart = Cart.objects.from_request(request, create=True)
    
    # make cart empty
    cart.empty()
    return HttpResponseRedirect(urlresolvers.reverse('satchmo_cart'))
