import json

from oscar.apps.checkout.views import *
import requests


class PaymentDetailsView(PaymentDetailsView):
    template_name_preview = 'checkout/preview.html'
    preview = True

    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):

        info = {
            'order': {
                'customer': user.email,
                'order_total': {
                    'currency': order_total.currency,
                    'excl_tax': str(order_total.excl_tax)
                }
            }
        }
        response = requests.post('http://localhost:5000/order', json=info)
        data = json.loads(response.text)
        order_number = data['number']

        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = str(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)


class ThankYouView(ThankYouView):
    template_name = 'checkout/thank_you.html'
