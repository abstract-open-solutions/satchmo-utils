import random, optparse, sys, logging, httplib, urllib
from django.conf import settings
from datetime import datetime

from django.core.management.base import BaseCommand

from satchmo_store.shop.models import Order


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-d", "--debug",
            action = "count",
            dest = "debug_level",
            default = 0,
            help = ("Shows debug log, multiple uses of the option "
                    "increase the verboseness")
        ),
        optparse.make_option(
            "-l", "--logfile",
            action = "store",
            dest = "logfile",
            default = "",
            metavar = "FILE",
            help = ("logs into FILE. If not given defaults to stderr")
        ),
        optparse.make_option(
            "-o", "--order-id",
            action = "store",
            dest = "order_id",
            default = "",
            metavar = "ORDER_ID",
            help = ("ID of a existing order")
        ),
    )
    help = ("""Simulate PayPal IPN process for given order.
You must configure 'http://localhost:8000/test_confirm_ipn/' url in 
PayPal URL Post Test settings in /settings view.""")

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def setupLogging(self, options):
        kwargs = {
            'level' : 50 - (options['debug_level'] * 10),
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
        if options.get('logfile', ''):
            kwargs['filename'] = options['logfile']
        else:
            kwargs['stream'] = sys.stderr
        logging.basicConfig(**kwargs)
        if options.get('output', ''):
            return open(options['output'], 'ab')
        else:
            return sys.stdout

    def handle(self, *args, **options):
        """
        """
        output = self.setupLogging(options)

        start = datetime.now()
        output.write("IPN testing STARTED At: %s\n" % start.strftime("%d/%m/%Y %H:%M:%S"))
        
        order_id = options.get("order_id")
        if not order_id.isdigit():
            output.write("Order %s does not exist. Enter valid order id\n" % order_id)
            end = datetime.now()
            output.write("IPN testing ENDED At: %s\n" % end.strftime("%d/%m/%Y %H:%M:%S"))
            return False
            
        order_id = int(order_id)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            output.write("Order %s does not exist. Enter valid order id\n" % order_id)
            end = datetime.now()
            output.write("IPN testing ENDED At: %s\n" % end.strftime("%d/%m/%Y %H:%M:%S"))
            return False
        
        # Check if order is payed thru PayPal
        # XXX: It should be a good thing if PayPal payment processor's
        # "ipn" view makes same control onto given order
        txn_id = random.randint(0, 10)
        payments = order.payments.all().order_by('id')
        if payments and (payments[0].payment == u"PAYPAL"):
            first_payment = payments[0]
            txn_id = first_payment.transaction_id
        else:
            output.write("Order %s isn't pay thru PayPal\n" % order_id)
            end = datetime.now()
            output.write("IPN testing ENDED At: %s\n" % end.strftime("%d/%m/%Y %H:%M:%S"))
            return False
        
        site_domain = settings.SITE_DOMAIN
        url = '/checkout/paypal/ipn/'
        params = urllib.urlencode({
            'payment_status': 'Completed',
            'invoice': order.id,
            'mc_gross': order.total,
            'txn_id': txn_id
        })
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }

        conn = httplib.HTTPConnection(site_domain, 8000)
        conn.request('POST', url, params, headers)
        response = conn.getresponse()
        import pdb; pdb.set_trace( )
        output.write("%s %s\n" % (response.status, response.reason))
        conn.close()
        
        end = datetime.now()
        output.write("IPN testing ENDED At: %s\n" % end.strftime("%d/%m/%Y %H:%M:%S"))
        return 'THE END'