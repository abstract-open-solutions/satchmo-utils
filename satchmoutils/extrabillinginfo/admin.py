from django.contrib import admin
from satchmoutils.models import ContactAdministrativeInformation


class ContactAdministrativeInformationOptions(admin.ModelAdmin):
    __name__ = "ContactAdministrativeInformation Options"

    search_fields = ['contact__first_name', 'contact__last_name']


admin.site.register(
    ContactAdministrativeInformation,
    ContactAdministrativeInformationOptions
)
