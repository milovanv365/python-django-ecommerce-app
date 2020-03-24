import oscar.apps.checkout.apps as apps
from oscar.core.loading import get_class
from django.conf.urls import url


class CheckoutConfig(apps.CheckoutConfig):
    name = 'apps.checkout'

    def ready(self):
        self.index_view = get_class('checkout.views', 'IndexView')
        self.shipping_address_view = get_class('checkout.views', 'ShippingAddressView')
        self.user_address_update_view = get_class('checkout.views',
                                                  'UserAddressUpdateView')
        self.user_address_delete_view = get_class('checkout.views',
                                                  'UserAddressDeleteView')
        self.shipping_method_view = get_class('checkout.views', 'ShippingMethodView')
        self.payment_method_view = get_class('checkout.views', 'PaymentMethodView')
        self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')
        self.thankyou_view = get_class('checkout.views', 'ThankYouView')

