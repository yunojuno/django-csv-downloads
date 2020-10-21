from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest

from .csv import write_csv
from .models import CsvDownload


def download_csv(
    request: HttpRequest, filename: str, queryset: QuerySet, *columns: str
) -> HttpResponse:
    """
    Download queryset as a CSV.

    This function creates the HttpResponse and tracks the download against
    the request.real_user, giving an audit trail of downloads.

    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    row_count = write_csv(response, queryset, *columns)
    response["X-Row-Count"] = row_count
    CsvDownload.objects.create(
        user=request.user,
        row_count=row_count,
        filename=filename,
        columns=", ".join(columns),
    )
    return response
