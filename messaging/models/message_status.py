from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserMessageStatus(models.Model):
    label = models.CharField(
        verbose_name=_('Message satus label'),
        max_length=30
    )

    class Meta:
        db_table  = 'messaging_ref_message_status'
        verbose_name = _('Message status')
        verbose_name_plural = _('Messages status')

    def __str__(self):
        return self.label
