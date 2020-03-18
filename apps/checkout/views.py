from django.urls import reverse_lazy
from oscar.apps.checkout import views


class PaymentDetailsView(views.PaymentDetailsView):
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid']

    preview = True
