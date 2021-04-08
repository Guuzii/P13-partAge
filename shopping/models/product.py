from django.db import models
from django.utils.translation import ugettext_lazy as _


class Product(models.Model):
    label = models.CharField(
        verbose_name=_('Product label'),
        max_length=50
    )
    description = models.TextField(
        verbose_name=_('Product description'),
    )
    price = models.SmallIntegerField(
        verbose_name=_('Product price')
    )
    xp_amount = models.IntegerField(
        verbose_name=_('Product xp amount'),
        null=True
    )
    path_to_sprite = models.CharField(
        verbose_name=_('Product path to sprite'),
        max_length=150,
        blank=True,
        null=True
    )
    is_multiple = models.BooleanField(
        verbose_name=_('Product can be bought multiple times'),
        default=False
    )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.label
