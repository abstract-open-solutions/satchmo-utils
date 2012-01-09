from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    (r'^cart/empty/$', 'satchmoutils.emptycart.views.cart_empty', {},
     'satchmo_cart_empty'),
)
