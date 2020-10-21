from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _lazy


class CsvDownload(models.Model):
    """Track CSV downloads."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        help_text="User who initiated the download.",
    )
    filename = models.CharField(max_length=100)
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text=_lazy("When the download took place.")
    )
    row_count = models.IntegerField(
        null=True, blank=True, help_text=_lazy("Rows downloaded")
    )
    columns = models.CharField(
        max_length=500, help_text=_lazy("The list of column headers in the download")
    )

    class Meta:
        verbose_name = "CSV Download"

    def __str__(self) -> str:
        return f"{self.filename}"
