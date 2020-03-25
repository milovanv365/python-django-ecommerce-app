from oscar.apps.checkout.mixins import *


class OrderPlacementMixin(OrderPlacementMixin):
    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.

        Override this view if you want to perform custom actions when an
        order is submitted.
        """
        # Send confirmation message (normally an email)
        # self.send_confirmation_message(order, self.communication_type_code)

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id

        response = HttpResponseRedirect(self.get_success_url())
        self.send_signal(self.request, response, order)
        return response
