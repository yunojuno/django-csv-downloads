from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views import View

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


class DownloadForbidden(Exception):
    pass


class DownloadCsv(View):
    """CBV for downloading CSVs."""

    # list of columns to be extracted from the queryset
    csv_columns = []

    def authorize(self, request: HttpRequest) -> None:
        """
        Authorize the download request.

        Raise DownloadForbidden if download is not permitted.

        Default is to allow all authenticated users access.

        """
        if not request.user.is_authenticated:
            raise DownloadForbidden()

    def filename(self, request: HttpRequest) -> str:
        """Return download filename."""
        raise NotImplementedError()

    def queryset(self, request: HttpRequest) -> QuerySet:
        """Fetch the appropriate data for the user."""
        raise NotImplementedError()

    def get(self, request: HttpRequest) -> HttpResponse:
        """Download bookings as CSV."""
        if not self.csv_columns:
            raise ValueError("DownloadCsv subclass must specify csv_columns")
        try:
            self.authorize(request)
        except DownloadForbidden:
            return HttpResponseForbidden()
        return download_csv(
            request.user,
            self.filename(),
            self.queryset(request),
            *self.csv_columns
        )
