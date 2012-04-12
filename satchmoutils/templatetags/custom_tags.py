from django import template
from django.conf import settings

from ..formextender import import_path

register = template.Library()


@register.inclusion_tag('tags/admin_extra_links.html', takes_context=True)
def admin_extra_links(context):
    """Reads the setting ``SATCHMO_SETTINGS['EXTRA_LINKS']``, which is a
    list of apps in the form ``dotted.name.of.module:Class``, and loads
    them
    """
    satchmo_settings = getattr(settings, 'SATCHMO_SETTINGS', {})
    admin_extra_links = []
    extenders = [
        import_path(p) for p in satchmo_settings.get('EXTRA_LINKS', [])]
    for extender in extenders:
        admin_extra_links.extend(
            extender.get_admin_links())
    return {'admin_extra_links': admin_extra_links}
