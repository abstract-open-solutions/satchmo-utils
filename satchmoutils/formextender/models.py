from django.conf import settings


extenders = getattr(settings, 'SATCHMO_SETTINGS', {}).get('FORM_EXTENDERS', [])
for extender in extenders:
    extender.extend()
