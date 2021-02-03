from typing import Sequence

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
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

    def has_permission(self, request: HttpRequest) -> bool:
        """Return True if the user has permission to download this file."""
        return True

    def get_user(self, request: HttpRequest) -> settings.AUTH_USER_MODEL:
        """
        Return the user against whom to record the download.

        This is provided for cases where the request.user may not be the
        user you wish to record the download against. Impersonation is the
        canonical use case for overriding this.

        """
        return request.user

    def get_filename(self, request: HttpRequest) -> str:
        """Return download filename."""
        raise NotImplementedError

    def get_columns(self, request: HttpRequest) -> Sequence[str]:
        """Return columns to extract from the queryset."""
        raise NotImplementedError

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Return the data to be downloaded."""
        raise NotImplementedError

    def get(self, request: HttpRequest) -> HttpResponse:
        """Download data as CSV."""
        if not self.has_permission(request):
            raise PermissionDenied

        return download_csv(
            self.get_user(request),
            self.get_filename(request),
            self.get_queryset(request),
            *self.get_columns(request),
        )
