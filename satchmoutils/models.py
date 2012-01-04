from django.utils.translation import ugettext_lazy as _
from django.db import models
from satchmo_store.contact import models as contact_models

# load custom configs
import config


class ContactAdministrativeInformation(models.Model):
    contact = models.OneToOneField(
        contact_models.Contact,
        verbose_name = _("contact")
    )
    business_number = models.CharField(
        _("business number"),
        max_length = 256
    )
    person_number = models.CharField(
        _("person number"),
        max_length = 256
    )
        
    def __unicode__(self):
        return _("administrative information for %(contact_name)s") % {
            'contact_name': self.contact.full_name
        }

    class Meta:
        verbose_name = _("administrative information")
        verbose_name_plural = _("administrative informations")
