from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    (r'^contactus/$', 'satchmoutils.contactus.views.contactus', {}, 'contactus'),
    (r'^contactus/submit/$', 'satchmoutils.contactus.views.contactus_action', {},
     'contactus_action'),
    (r"^captcha/", include('captcha.urls')),
)
