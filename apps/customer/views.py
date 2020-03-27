from oscar.apps.customer.views import *


class AccountAuthView(AccountAuthView):
    template_name = 'customer/login_registration.html'


class AccountRegistrationView(AccountRegistrationView):
    template_name = 'customer/registration.html'
