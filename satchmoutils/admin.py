from django.contrib import admin
from satchmoutils.models import ContactAdministrativeInformation, ContactExtraAddressInformation


class ContactAdministrativeInformationOptions(admin.ModelAdmin):
    __name__ = "ContactAdministrativeInformation Options"

    search_fields = ['contact__first_name', 'contact__last_name']

class ContactExtraAddressInformationOptions(admin.ModelAdmin):
    __name__ = "ContactExtraAddressInformation Options"

    search_fields = ['contact__first_name', 'contact__last_name']

admin.site.register(
    ContactAdministrativeInformation, 
    ContactAdministrativeInformationOptions
)

admin.site.register(
    ContactExtraAddressInformation, 
    ContactExtraAddressInformationOptions
)
