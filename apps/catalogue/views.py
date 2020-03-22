import json
import requests
from oscar.apps.catalogue.views import CatalogueView
from oscar.core.loading import get_model
from django import shortcuts


class CatalogueView(CatalogueView):
    template_name = 'catalogue/browse.html'
    # product_model = get_model('catalogue', 'product')
    # products = shortcuts.get_list_or_404(product_model)
    #
    # def get(self, request, *args, **kwargs):
    #     for product in self.products:
    #         upc = product.upc
    #         url = 'http://localhost:5000/stock/{}'.format(upc)
    #         response = requests.post(url)
    #         data = json.loads(response.text)
    #         price = data['price']
    #
    #         original_product = product.stockrecords.first()
    #         original_product.price_excl_tax = price
    #         original_product.save()
