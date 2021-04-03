from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


class ProductTransaction(models.Model):
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('shopping.Product', on_delete=models.PROTECT)
    created_at = models.DateTimeField(
        verbose_name=_('Transaction creation date'),
        default=now
    )

    class Meta:
        verbose_name = _('Product transaction')
        verbose_name_plural = _('Product transactions')

    def __str__(self):
        return self.product
