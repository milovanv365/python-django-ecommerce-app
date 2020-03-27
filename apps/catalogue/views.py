from oscar.apps.catalogue.views import *


class CatalogueView(CatalogueView):
    template_name = 'catalogue/browse.html'


class ProductDetailView(ProductDetailView):
    template_name = 'catalogue/detail.html'
