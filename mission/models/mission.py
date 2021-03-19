from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


class Mission(models.Model):
    bearer_user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE, related_name='bearer_user')
    acceptor_user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE, related_name='acceptor_user', null=True)
    status = models.ForeignKey('mission.MissionStatus', on_delete=models.PROTECT)
    category = models.ForeignKey('mission.MissionCategory', on_delete=models.PROTECT)
    bonus_reward = models.ForeignKey('mission.MissionBonusReward', on_delete=models.PROTECT)
    created_at = models.DateTimeField(
        verbose_name=_('Mission creation date'),
        default=now
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Mission update date'),
        null=True
    )
    title = models.CharField(
        verbose_name=_('Mission title'),
        max_length=50
    )
    description = models.TextField(
        verbose_name=_('Mission description')
    )

    class Meta:
        verbose_name = _('Mission')
        verbose_name_plural = _('Missions')

    def __str__(self):
        return self.title
