from oscar.apps.checkout import views
import requests


class PaymentDetailsView(views.PaymentDetailsView):
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
    ]

    template_name_preview = 'checkout/preview.html'
    preview = True

    def post(self, request, *args, **kwargs):
        info = {'order': {'customer': 'peter', 'item': '21456'}}
        response = requests.post('http://localhost:5000/order', json=info)
        print(response.text)

        return self.render_preview(request)
