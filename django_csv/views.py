from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpResponse

from .csv import write_csv
from .models import CsvDownload


def download_csv(
    user: settings.AUTH_USER_MODEL, filename: str, queryset: QuerySet, *columns: str
) -> HttpResponse:
    """Download queryset as a CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    row_count = write_csv(response, queryset, *columns)
    response["X-Row-Count"] = row_count
    CsvDownload.objects.create(
        user=user,
        row_count=row_count,
        filename=filename,
        columns=", ".join(columns),
    )
    return response
