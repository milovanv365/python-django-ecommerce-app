from oscar.apps.catalogue.abstract_models import *
from django.utils.translation import gettext_lazy as _


class AbstractProduct(models.Model):
    """
    The base product object

    There's three kinds of products; they're distinguished by the structure
    field.

    - A stand alone product. Regular product that lives by itself.
    - A child product. All child products have a parent product. They're a
      specific version of the parent.
    - A parent product. It essentially represents a set of products.

    An example could be a yoga course, which is a parent product. The different
    times/locations of the courses would be associated with the child products.
    """
    STANDALONE, PARENT, CHILD = 'standalone', 'parent', 'child'
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    structure = models.CharField(
        _("Product structure"), max_length=10, choices=STRUCTURE_CHOICES,
        default=STANDALONE)

    is_public = models.BooleanField(
        _('Is public'),
        default=True,
        help_text=_("Show this product in search results and catalogue listings."))

    upc = NullCharField(
        _("UPC"), max_length=64, blank=True, null=True, unique=True,
        help_text=_("Universal Product Code (UPC) is an identifier for "
                    "a product which is not specific to a particular "
                    " supplier. Eg an ISBN for a book."))

    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_("Parent product"),
        help_text=_("Only choose a parent product if you're creating a child "
                    "product.  For example if this is a size "
                    "4 of a particular t-shirt.  Leave blank if this is a "
                    "stand-alone product (i.e. there is only one version of"
                    " this product)."))

    # Title is mandatory for canonical products but optional for child products
    title = models.CharField(pgettext_lazy('Product title', 'Title'),
                             max_length=255, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, unique=False)
    description = models.TextField(_('Description'), blank=True)

    #: "Kind" of product, e.g. T-Shirt, Book, etc.
    #: None for child products, they inherit their parent's product class
    product_class = models.ForeignKey(
        'catalogue.ProductClass',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Product type'), related_name="products",
        help_text=_("Choose what type of product this is"))
    attributes = models.ManyToManyField(
        'catalogue.ProductAttribute',
        through='ProductAttributeValue',
        verbose_name=_("Attributes"),
        help_text=_("A product attribute is something that this product may "
                    "have, such as a size, as specified by its class"))
    #: It's possible to have options product class-wide, and per product.
    product_options = models.ManyToManyField(
        'catalogue.Option', blank=True, verbose_name=_("Product options"),
        help_text=_("Options are values that can be associated with a item "
                    "when it is added to a customer's basket.  This could be "
                    "something like a personalised message to be printed on "
                    "a T-shirt."))

    recommended_products = models.ManyToManyField(
        'catalogue.Product', through='ProductRecommendation', blank=True,
        verbose_name=_("Recommended products"),
        help_text=_("These are products that are recommended to accompany the "
                    "main product."))

    # Denormalised product rating - used by reviews app.
    # Product has no ratings if rating is None
    rating = models.FloatField(_('Rating'), null=True, editable=False)

    date_created = models.DateTimeField(
        _("Date created"), auto_now_add=True, db_index=True)

    # This field is used by Haystack to reindex search
    date_updated = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True)

    categories = models.ManyToManyField(
        'catalogue.Category', through='ProductCategory',
        verbose_name=_("Categories"))

    #: Determines if a product may be used in an offer. It is illegal to
    #: discount some types of product (e.g. ebooks) and this field helps
    #: merchants from avoiding discounting such products
    #: Note that this flag is ignored for child products; they inherit from
    #: the parent product.
    is_discountable = models.BooleanField(
        _("Is discountable?"), default=True, help_text=_(
            "This flag indicates if this product can be used in an offer "
            "or not"))

    objects = ProductQuerySet.as_manager()
    # browsable property is deprecated and will be removed in Oscar 2.1
    # Use Product.objects.browsable() instead.
    browsable = BrowsableProductManager()

    class Meta:
        abstract = True
        app_label = 'catalogue'
        ordering = ['-date_created']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attr = ProductAttributesContainer(product=self)

    def __str__(self):
        if self.title:
            return self.title
        if self.attribute_summary:
            return "%s (%s)" % (self.get_title(), self.attribute_summary)
        else:
            return self.get_title()

    def get_absolute_url(self):
        """
        Return a product's absolute URL
        """
        return reverse('catalogue:detail',
                       kwargs={'product_slug': self.slug, 'pk': self.id})

    def clean(self):
        """
        Validate a product. Those are the rules:

        +---------------+-------------+--------------+--------------+
        |               | stand alone | parent       | child        |
        +---------------+-------------+--------------+--------------+
        | title         | required    | required     | optional     |
        +---------------+-------------+--------------+--------------+
        | product class | required    | required     | must be None |
        +---------------+-------------+--------------+--------------+
        | parent        | forbidden   | forbidden    | required     |
        +---------------+-------------+--------------+--------------+
        | stockrecords  | 0 or more   | forbidden    | 0 or more    |
        +---------------+-------------+--------------+--------------+
        | categories    | 1 or more   | 1 or more    | forbidden    |
        +---------------+-------------+--------------+--------------+
        | attributes    | optional    | optional     | optional     |
        +---------------+-------------+--------------+--------------+
        | rec. products | optional    | optional     | unsupported  |
        +---------------+-------------+--------------+--------------+
        | options       | optional    | optional     | forbidden    |
        +---------------+-------------+--------------+--------------+

        Because the validation logic is quite complex, validation is delegated
        to the sub method appropriate for the product's structure.
        """
        getattr(self, '_clean_%s' % self.structure)()
        if not self.is_parent:
            self.attr.validate_attributes()

    def _clean_standalone(self):
        """
        Validates a stand-alone product
        """
        if not self.title:
            raise ValidationError(_("Your product must have a title."))
        if not self.product_class:
            raise ValidationError(_("Your product must have a product class."))
        if self.parent_id:
            raise ValidationError(_("Only child products can have a parent."))

    def _clean_child(self):
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        if self.product_class:
            raise ValidationError(
                _("A child product can't have a product class."))
        if self.pk and self.categories.exists():
            raise ValidationError(
                _("A child product can't have a category assigned."))
        # Note that we only forbid options on product level
        if self.pk and self.product_options.exists():
            raise ValidationError(
                _("A child product can't have options."))

    def _clean_parent(self):
        """
        Validates a parent product.
        """
        self._clean_standalone()
        if self.has_stockrecords:
            raise ValidationError(
                _("A parent product can't have stockrecords."))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_title())
        super().save(*args, **kwargs)
        self.attr.save()

    # Properties

    @property
    def is_standalone(self):
        return self.structure == self.STANDALONE

    @property
    def is_parent(self):
        return self.structure == self.PARENT

    @property
    def is_child(self):
        return self.structure == self.CHILD

    def can_be_parent(self, give_reason=False):
        """
        Helps decide if a the product can be turned into a parent product.
        """
        reason = None
        if self.is_child:
            reason = _('The specified parent product is a child product.')
        if self.has_stockrecords:
            reason = _(
                "One can't add a child product to a product with stock"
                " records.")
        is_valid = reason is None
        if give_reason:
            return is_valid, reason
        else:
            return is_valid

    @property
    def options(self):
        """
        Returns a set of all valid options for this product.
        It's possible to have options product class-wide, and per product.
        """
        pclass_options = self.get_product_class().options.all()
        return pclass_options | self.product_options.all()

    @cached_property
    def has_options(self):
        # Extracting annotated value with number of product class options
        # from product list queryset.
        has_product_class_options = getattr(self, 'has_product_class_options', None)
        has_product_options = getattr(self, 'has_product_options', None)
        if has_product_class_options is not None and has_product_options is not None:
            return has_product_class_options or has_product_options
        return self.get_product_class().options.exists() or self.product_options.exists()

    @property
    def is_shipping_required(self):
        return self.get_product_class().requires_shipping

    @property
    def has_stockrecords(self):
        """
        Test if this product has any stockrecords
        """
        return self.stockrecords.exists()

    @property
    def num_stockrecords(self):
        return self.stockrecords.count()

    @property
    def attribute_summary(self):
        """
        Return a string of all of a product's attributes
        """
        attributes = self.attribute_values.all()
        pairs = [attribute.summary() for attribute in attributes]
        return ", ".join(pairs)

    def get_title(self):
        """
        Return a product's title or it's parent's title if it has no title
        """
        title = self.title
        if not title and self.parent_id:
            title = self.parent.title
        return title
    get_title.short_description = pgettext_lazy("Product title", "Title")

    def get_product_class(self):
        """
        Return a product's item class. Child products inherit their parent's.
        """
        if self.is_child:
            return self.parent.product_class
        else:
            return self.product_class
    get_product_class.short_description = _("Product class")

    def get_is_discountable(self):
        """
        At the moment, :py:attr:`.is_discountable` can't be set individually for child
        products; they inherit it from their parent.
        """
        if self.is_child:
            return self.parent.is_discountable
        else:
            return self.is_discountable

    def get_categories(self):
        """
        Return a product's categories or parent's if there is a parent product.
        """
        if self.is_child:
            return self.parent.categories
        else:
            return self.categories
    get_categories.short_description = _("Categories")

    # Images

    def get_missing_image(self):
        """
        Returns a missing image object.
        """
        # This class should have a 'name' property so it mimics the Django file
        # field.
        return MissingProductImage()

    def get_all_images(self):
        if self.is_child and not self.images.exists():
            return self.parent.images.all()
        return self.images.all()

    def primary_image(self):
        """
        Returns the primary image for a product. Usually used when one can
        only display one product image, e.g. in a list of products.
        """

        return 'http://localhost:5000/picture/{}'.format(self.upc)

    # Updating methods

    def update_rating(self):
        """
        Recalculate rating field
        """
        self.rating = self.calculate_rating()
        self.save()
    update_rating.alters_data = True

    def calculate_rating(self):
        """
        Calculate rating value
        """
        result = self.reviews.filter(
            status=self.reviews.model.APPROVED
        ).aggregate(
            sum=Sum('score'), count=Count('id'))
        reviews_sum = result['sum'] or 0
        reviews_count = result['count'] or 0
        rating = None
        if reviews_count > 0:
            rating = float(reviews_sum) / reviews_count
        return rating

    def has_review_by(self, user):
        if user.is_anonymous:
            return False
        return self.reviews.filter(user=user).exists()

    def is_review_permitted(self, user):
        """
        Determines whether a user may add a review on this product.

        Default implementation respects OSCAR_ALLOW_ANON_REVIEWS and only
        allows leaving one review per user and product.

        Override this if you want to alter the default behaviour; e.g. enforce
        that a user purchased the product to be allowed to leave a review.
        """
        if user.is_authenticated or settings.OSCAR_ALLOW_ANON_REVIEWS:
            return not self.has_review_by(user)
        else:
            return False

    @cached_property
    def num_approved_reviews(self):
        return self.reviews.approved().count()

    @property
    def sorted_recommended_products(self):
        """Keeping order by recommendation ranking."""
        return [r.recommendation for r in self.primary_recommendations
                                              .select_related('recommendation').all()]



