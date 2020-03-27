from django import shortcuts
from oscar.apps.catalogue.views import *


class CatalogueView(CatalogueView):
    template_name = 'catalogue/browse.html'
    # product_model = get_model('catalogue', 'product')
    # products = shortcuts.get_list_or_404(product_model)
    #
    # for product in products:
    #     upc = product.upc
    #     image_url = 'http://localhost:5000/picture/{}'.format(upc)
    #
    #     original_image = product.images.first()
    #     original_image.original = image_url
    #     original_image.save()


class ProductDetailView(ProductDetailView):
    template_name = 'catalogue/detail.html'
