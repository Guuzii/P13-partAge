from django.db import models
from django.utils.translation import ugettext_lazy as _

class UserType(models.Model):
    label = models.CharField(
        verbose_name=_('Type label'),
        max_length=30,
    )

    class Meta:
        db_table  = 'user_ref_user_type'
        verbose_name = _('User type')
        verbose_name_plural = _('User types')

    def __str__(self):
        return self.label