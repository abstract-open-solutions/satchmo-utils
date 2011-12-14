from django.conf import settings
from django.conf.urls.defaults import *
from satchmo_store.shop import get_satchmo_setting
from django.views.generic.simple import direct_to_template

catbase = r'^' + get_satchmo_setting('CATEGORY_SLUG') + '/'
prodbase = r'^' + get_satchmo_setting('PRODUCT_SLUG') + '/'

urlpatterns = patterns('',
    (r'^cart/$', 'satchmoutils.views.display_cart', {}, 'satchmo_cart'),
    (r'^cart/add/$', 'satchmoutils.views.cart_add', {}, 'satchmo_cart_add'),
    (r'^cart/empty/$', 'satchmoutils.views.cart_empty', {}, 'satchmo_cart_empty'),
    (r'^add/$', 'satchmoutils.views.smart_add', {}, 'satchmo_smart_add'),
    (r"^captcha/", include('captcha.urls')),
)