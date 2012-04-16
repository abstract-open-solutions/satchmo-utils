from django.conf import settings
from livesettings import config_value
from satchmo_store.shop.models import Config


class ShopUtils(object):
    """Utility to retrieve the shop configuration.
    """

    def schema(self):
        schema = {
            'shop_name': (
                ('SHOP_CONFIG', 'SHOP_NAME'),
                'store_name'),
            'shop_email': (
                ('SHOP_CONFIG', 'EMAIL'),
                'store_email'),
            'shop_iban': (
                ('SHOP_CONFIG', 'IBAN'),
                None),
            'shop_address': (
                ('SHOP_CONFIG', 'ADDRESS'),
                'street1'),
            'shop_zipcode': (
                ('SHOP_CONFIG', 'ZIP_CODE'),
                'postal_code'),
            'shop_city': (
                ('SHOP_CONFIG', 'CITY'),
                'city'),
            'shop_vat': (
                ('SHOP_CONFIG', 'VAT'),
                None),
            'shop_telephone': (
                ('SHOP_CONFIG', 'TELEPHONE'),
                'phone'),
            'shop_fax': (
                ('SHOP_CONFIG', 'FAX'),
                None)}
        schema.update(getattr(settings, 'SHOP_CONFIG_SCHEMA', {}))
        return schema

    def get_shop_config(self):
        shop_config = Config.objects.get_current()
        schema = self.schema()
        config = {}
        for key in schema.keys():
            config_path, config_attribute = schema[key]
            value = config_value(*config_path)
            if not value and config_attribute is not None:
                value = getattr(shop_config, config_attribute, None)
            config[key] = value
        return config
