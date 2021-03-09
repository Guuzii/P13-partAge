from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


class UserMessage(models.Model):
    sender_user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE, related_name='sender_user')
    receiver_user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE, related_name='receiver_user')
    status = models.ForeignKey('messaging.UserMessageStatus', on_delete=models.PROTECT)
    is_support = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        verbose_name=_('Message creation date'),
        default=now
    )
    content = models.CharField(
        verbose_name=_('Message content'),
        max_length=255,
    )

    class Meta:
        db_table  = 'messaging_message'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.content
