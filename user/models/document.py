from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class Document(models.Model):
    created_at = models.DateField(
        verbose_name=_('Document creation date'),
        default=timezone.now
    )
    path = models.CharField(
        verbose_name=_('Path to file'),
        max_length=150,
    )
    is_valid = models.BooleanField(default=False)

    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)
    document_type = models.ForeignKey('user.DocumentType', on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __str__(self):
        return self.document_type.label