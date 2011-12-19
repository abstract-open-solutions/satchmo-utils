from livesettings import config_register, ConfigurationGroup, StringValue
from django.utils.translation import ugettext_lazy as _


# Shop configs
SHOP_INFO = ConfigurationGroup(
    'SHOP_INFO',
    _('Shop info'),
    ordering=1 
    )
    
config_register(
    StringValue(
        SHOP_INFO,
        'IBAN_CODE',
        description = _('IBAN code'),
        help_text = "",
        default = "iban"
    )
)

config_register(
    StringValue(
        SHOP_INFO,
        'VAT_NUMBER',
        description = _('VAT number'),
        help_text = "",
        default = "vat"
    )
)