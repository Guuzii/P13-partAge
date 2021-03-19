from django.db import models
from django.utils.translation import ugettext_lazy as _


class MissionCategory(models.Model):
    label = models.CharField(
        verbose_name=_('Mission category label'),
        max_length=30
    )
    base_reward_amount = models.SmallIntegerField(
        verbose_name=_('Mission category base reward')
    )

    class Meta:
        db_table  = 'mission_ref_mission_category'
        verbose_name = _('Mission category')
        verbose_name_plural = _('Mission categories')

    def __str__(self):
        return self.label
