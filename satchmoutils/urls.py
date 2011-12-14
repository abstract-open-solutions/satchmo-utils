from django.conf import settings
from django.conf.urls.defaults import *
from satchmo_store.shop import get_satchmo_setting
from django.views.generic.simple import direct_to_template

catbase = r'^' + get_satchmo_setting('CATEGORY_SLUG') + '/'
prodbase = r'^' + get_satchmo_setting('PRODUCT_SLUG') + '/'

urlpatterns = patterns('',
    (r'^cart/empty/$', 'satchmoutils.views.cart_empty', {}, 'satchmo_cart_empty'),
    (r'^contactus/$', 'satchmoutils.views.contacts', {}, 'primifrutti_contacts'),
    (r'^contacts/submit/$', 'satchmoutils.views.contacts_action', {}, 'primifrutti_contacts_action'),
    (r"^captcha/", include('captcha.urls')),
)