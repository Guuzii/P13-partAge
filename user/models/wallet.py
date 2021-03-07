from django.db import models
from django.utils.translation import ugettext_lazy as _


class Wallet(models.Model):
    balance = models.IntegerField(
        verbose_name=_('Wallet balance'),
        default=0
    )

    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')

    def __str__(self):
        return str(self.balance)
