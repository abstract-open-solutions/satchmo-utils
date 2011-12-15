from decimal import Decimal
from keyedcache import cache_delete
from livesettings import config_get

from l10n.models import Country
from django.test import TestCase
from django.contrib.sites.models import Site
from satchmo_store.contact.models import Contact, ContactRole, AddressBook
from satchmo_store.shop.models import Order, OrderItem
from product.models import Product

import logging

log = logging.getLogger('satchmoutils.tax.modules.noarea.test')


def make_test_order(country, state, site=None, price=None, quantity=5):
    if not site:
        site = Site.objects.get_current()
    c = Contact(first_name="Tax", last_name="Tester",
        role=ContactRole.objects.get(pk='Customer'), email="tax@example.com")
    c.save()
    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact = country)

    ad = AddressBook(contact=c, description="home",
        street1 = "test", state=state, city="Napoli",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    o = Order(contact=c, shipping_cost=Decimal('10.00'), site = site)
    o.save()

    p = Product.objects.get(slug='formaggio-fresco-di-carmasciano')
    item1 = OrderItem(order=o, product=p, quantity=quantity,
        unit_price=price, line_item_price=price*quantity)
    item1.save()

    return o
    
class TaxTest(TestCase):

    def tearDown(self):
        cache_delete()

    def testNoArea(self):
        """Test No-Area tax module"""
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmoutils.tax.modules.noarea')

        order = make_test_order('IT', '', site=None, price=Decimal('10.00'), quantity=5)

        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax

        self.assertEqual(subtotal, Decimal('50.00'))
        self.assertEqual(tax, Decimal('10.50'))
        # 50 + 10 shipping + 10.5 (21% on 50) tax
        self.assertEqual(price, Decimal('70.50'))

        taxes = order.taxes.all()
        self.assertEqual(2, len(taxes))
        t1 = taxes[0]
        t2 = taxes[1]
        self.assert_('Shipping' in (t1.description, t2.description))
        if t1.description == 'Shipping':
            tship = t1
            tmain = t2
        else:
            tship = t2
            tmain = t1
        self.assertEqual(tmain.tax, Decimal('10.50'))
        self.assertEqual(tship.tax, Decimal('0.00'))
