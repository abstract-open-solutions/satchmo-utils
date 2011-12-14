from django.conf.urls.defaults import patterns
from livesettings import config_get_group
from satchmo_store.shop.satchmo_settings import get_satchmo_setting
ssl = get_satchmo_setting('SSL', default_value=False)

config = config_get_group('PAYMENT_BONIFICO')

urlpatterns = patterns('',
    (r'^$', 'satchmoutils.payments.modules.bonifico.views.one_step', {'SSL': ssl}, 'BONIFICO_satchmo_checkout-step2'),
    (r'^suspended/$', 'satchmoutils.payments.views.suspended', {'SSL': ssl}, 'BONIFICO_satchmo_checkout-suspended'),
    (r'^success/$', 'satchmoutils.payments.modules.views.multisuccess_view', {'SSL': ssl}, 'BONIFICO_satchmo_checkout-success'),    
)