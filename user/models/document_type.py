from django.db import models
from django.utils.translation import ugettext_lazy as _


class DocumentType(models.Model):
    label = models.CharField(
        verbose_name=_('Document type label'),
        max_length=30
    )

    class Meta:
        db_table  = 'user_ref_document_type'
        verbose_name = _('Document type')
        verbose_name_plural = _('Document types')

    def __str__(self):
        return self.label
