import json
import requests

from oscar.apps.basket.views import *


class BasketView(BasketView):
    template_name = 'basket/basket.html'

    def json_response(self, ctx, flash_messages):
        basket_html = render_to_string(
            'basket/partials/basket_content.html',
            context=ctx, request=self.request)

        return JsonResponse({
            'content_html': basket_html,
            'messages': flash_messages.as_dict()
        })


class BasketAddView(BasketAddView):
    def post(self, request, *args, **kwargs):
        self.product = shortcuts.get_object_or_404(
            self.product_model, pk=kwargs['pk'])
        upc = self.product.upc
        url = 'http://localhost:5000/stock/{}'.format(upc)
        response = requests.post(url)
        data = json.loads(response.text)
        price = data['price']
        stock = data['stock']

        original_product = self.product.stockrecords.first()
        original_product.price_excl_tax = price
        original_product.num_in_stock = stock
        original_product.save()

        return super().post(request, *args, **kwargs)
