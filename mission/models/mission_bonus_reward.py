from django.db import models
from django.utils.translation import ugettext_lazy as _


class MissionBonusReward(models.Model):
    reward_amount = models.SmallIntegerField(
        verbose_name=_('Mission bonus reward amount')
    )
    description = models.CharField(
        verbose_name=_('Mission bonus reward description'),
        max_length=255
    )

    class Meta:
        verbose_name = _('Mission bonus reward')
        verbose_name_plural = _('Mission bonus rewards')

    def __str__(self):
        return self.description
