from django import template

register = template.Library()


def custom_addressblock(address, civicnumber):
    """Output an address as a HTML formatted text block"""
    return {"address" : address, 'civicnumber' : civicnumber}

register.inclusion_tag('contact/_custom_addressblock.html')(
    custom_addressblock
)
