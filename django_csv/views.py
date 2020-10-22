from typing import Sequence

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


class CsvDownloadView(View):
    """CBV for downloading CSVs."""

    def is_permitted(self, request: HttpRequest) -> bool:
        """Return True if the download is permitted."""
        raise NotImplementedError()

    def user(self, request: HttpRequest) -> settings.AUTH_USER_MODEL:
        """Return the user against whom to record the download."""
        return request.user

    def filename(self, request: HttpRequest) -> str:
        """Return download filename."""
        raise NotImplementedError()

    def columns(self, request: HttpRequest) -> Sequence[str]:
        """Return columns to extract from the queryset."""
        raise NotImplementedError()

    def queryset(self, request: HttpRequest) -> QuerySet:
        """Return the data to be downloaded."""
        raise NotImplementedError()

    def get(self, request: HttpRequest) -> HttpResponse:
        """Download data as CSV."""
        if not self.is_permitted(request):
            return HttpResponseForbidden()
        return download_csv(
            self.user(request),
            self.filename(request),
            self.queryset(request),
            *self.columns(request),
        )
