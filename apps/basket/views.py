import json
import requests

from oscar.apps.basket.views import *


class BasketAddView(BasketAddView):
    def post(self, request, *args, **kwargs):
        self.product = shortcuts.get_object_or_404(
            self.product_model, pk=kwargs['pk'])
        upc = self.product.upc
        url = 'http://localhost:5000/stock/{}'.format(upc)
        response = requests.post(url)
        data = json.loads(response.text)
        price = data['price']

        original_product = self.product.stockrecords.first()
        original_product.price_excl_tax = price
        original_product.save()

        return super().post(request, *args, **kwargs)
