from django.db import models
from django.utils.translation import ugettext_lazy as _


class MissionStatus(models.Model):
    label = models.CharField(
        verbose_name=_('Mission status label'),
        max_length=30
    )

    class Meta:
        db_table  = 'mission_ref_mission_status'
        verbose_name = _('Mission status')
        verbose_name_plural = _('Mission status')

    def __str__(self):
        return self.label
