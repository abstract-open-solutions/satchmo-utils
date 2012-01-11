from django.conf.urls.defaults import *
from satchmo_store.shop import get_satchmo_setting

catbase = r'^' + get_satchmo_setting('CATEGORY_SLUG') + '/'
prodbase = r'^' + get_satchmo_setting('PRODUCT_SLUG') + '/'

urlpatterns = patterns('',
    (r'^cart/empty/$', 'satchmoutils.views.cart_empty', {}, 'satchmo_cart_empty'),
    (r"^test_confirm_ipn/", 'satchmoutils.test_views.test_confirm_ipn', {}, 'test_confirm_ipn'),
    (r"^captcha/", include('captcha.urls')),
)
