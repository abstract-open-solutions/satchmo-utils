import keyedcache
from keyedcache import cache_delete
from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import Client
from l10n.models import *
from l10n.models import Country
from livesettings import config_get, config_get_group

from satchmo_store.contact.models import Contact, ContactRole, AddressBook
from satchmo_store.shop.models import Order, OrderItem
from satchmo_store.contact.models import *
from satchmo_store.shop.models import *

from product.models import *
from product.models import Product
from payment import utils


def make_test_order(country, state, site=None, orderitems=None):
    if not orderitems:
        orderitems = [
            ('formaggio-fresco-di-carmasciano', 5), 
        ]

    if not site:
        site = Site.objects.get_current()

    c = Contact(first_name="Order", last_name="Tester",
        role=ContactRole.objects.get(pk='Customer'), email="order@example.com")
    c.save()

    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact = country)

    ad = AddressBook(contact=c, description="home",
        street1 = "via prova 123", state=state, city="Napoli",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    o = Order(contact=c, shipping_cost=Decimal('10.00'), site = site)
    o.save()

    for slug, qty in orderitems:
        p = Product.objects.get(slug=slug)
        price = p.unit_price
        item = OrderItem(order=o, product=p, quantity=qty,
            unit_price=price, line_item_price=price*qty)
        item.save()

    return o
    
class TaxTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.IT = Country.objects.get(iso2_code__iexact = "IT")
        
    def tearDown(self):
        cache_delete()

    def testNoArea(self):
        """Test No-Area tax module"""
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmoutils.tax.modules.noarea')

        order = make_test_order(self.IT, '')

        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax

        self.assertEqual(subtotal, Decimal('50.00'))
        self.assertEqual(tax, Decimal('12.60'))
        # 50 + 10 shipping + 12.6 (21% on 50) tax
        self.assertEqual(price, Decimal('72.60'))

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
        self.assertEqual(tship.tax, Decimal('2.10'))

class TestModulesSettings(TestCase):

    def setUp(self):
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmoutils.tax.modules.noarea')

    def tearDown(self):
        keyedcache.cache_delete()

    def testGetBonifico(self):
        self.processor = config_get_group('PAYMENT_BONIFICO')
        self.assert_(self.processor != None)
        self.assertEqual(self.processor.LABEL, 'Bonifico')

    def testGetContrassegno(self):
        self.processor = config_get_group('PAYMENT_CONTRASSEGNO')
        self.assert_(self.processor != None)
        self.assertEqual(self.processor.LABEL, 'Pagamento alla consegna')
        self.assertEqual(self.processor.CURRENCY_CODE, '242') # Euro
        self.assertEqual(self.processor.HANDLING_COST, '4.00')
        
    def testGetCreditcard(self):
        self.processor = config_get_group('PAYMENT_CREDITCARD')
        self.assert_(self.processor != None)
        self.assertEqual(self.processor.LABEL, 'Creditcard (Bancasella)')
        self.assertEqual(self.processor.CURRENCY_CODE, '242') # Euro
        self.assertEqual(self.processor.POST_URL, 'https://ecomm.sella.it/gestpay/pagam.asp')
        self.assertEqual(self.processor.POST_TEST_URL, 'https://testecomm.sella.it/gestpay/pagam.asp')

class TestPaymentHandling(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml', 'initial_data.yaml']

    def setUp(self):
        self.client = Client()
        self.IT = Country.objects.get(iso2_code__iexact = "IT")
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmoutils.tax.modules.noarea')

    def tearDown(self):
        keyedcache.cache_delete()

    def test_bonifico(self):
        """Test making a capture without authorization using BONIFICO."""
        order = make_test_order(self.IT, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('72.60'))

        processor = utils.get_processor_by_key('PAYMENT_BONIFICO')
        processor.create_pending_payment(order=order, amount=order.total)

        processor.prepare_data(order)
        result = processor.capture_payment()
        self.assertEqual(result.success, True)
        pmt1 = result.payment
        self.assertEqual(type(pmt1), OrderPayment)

        self.assertEqual(order.authorized_remaining, Decimal('0.00'))

        self.assertEqual(result.success, True)
        payment = result.payment
        self.assertEqual(pmt1, payment)
        self.assertEqual(order.orderstatus_set.latest().status, 'New')
        self.assertEqual(order.balance, Decimal('0'))
        
    def test_contrassegno(self):
        """Test making a capture without authorization using CONTRASSEGNO."""
        order = make_test_order(self.IT, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('72.60'))

        processor = utils.get_processor_by_key('PAYMENT_CONTRASSEGNO')
        processor.create_pending_payment(order=order, amount=order.total)

        processor.prepare_data(order)
        result = processor.capture_payment()
        self.assertEqual(result.success, True)
        pmt1 = result.payment
        self.assertEqual(type(pmt1), OrderPayment)

        self.assertEqual(order.authorized_remaining, Decimal('0.00'))

        self.assertEqual(result.success, True)
        payment = result.payment
        self.assertEqual(pmt1, payment)
        self.assertEqual(order.orderstatus_set.latest().status, 'New')
        self.assertEqual(order.balance, Decimal('0'))
        
    def test_creditcard(self):
        """Test making a capture without authorization using CREDITCARD (Bancasella)."""
        order = make_test_order(self.IT, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('72.60'))
        
        processor = utils.get_processor_by_key('PAYMENT_CREDITCARD')
        processor.create_pending_payment(order=order, amount=order.total)

        self.assertEqual(order.pendingpayments.count(), 1)
        self.assertEqual(order.payments.count(), 1)

        pending = order.pendingpayments.all()[0]
        self.assertEqual(pending.amount, order.total)

        payment = order.payments.all()[0]
        self.assertEqual(payment.amount, Decimal('0'))

        self.assertEqual(pending.capture, payment)

        self.assertEqual(order.balance_paid, Decimal('0'))
        self.assertEqual(order.authorized_remaining, Decimal('0'))

        processor.prepare_data(order)
        result = processor.authorize_payment()
        self.assertEqual(result.success, False)
        
        processor.record_payment(
            order = order,
            amount = order.total,
            transaction_id = 'ABCDE12345',
            reason_code = '200'
        )
        if order.notes is None:
            order.notes = ""
        else:
            order.notes += "\n\n"
        order.save()
        order.add_status(
            status = 'New',
            notes = "Pagato mediante BANCASELLA"
        )
        
        self.assertEqual(order.authorized_remaining, Decimal('0'))
        self.assertEqual(order.orderstatus_set.latest().status, 'New')
        self.assertEqual(order.balance, Decimal('0'))
