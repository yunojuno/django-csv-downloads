from typing import Any, List, Type

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views import View

from .csv import BaseQuerySetWriter, BulkQuerySetWriter, write_csv
from .models import CsvDownload
from .settings import MAX_ROWS
from .types import OptionalSequence


def download_csv(
    user: settings.AUTH_USER_MODEL,
    filename: str,
    queryset: QuerySet,
    *columns: str,
    header: bool = True,
    max_rows: int = MAX_ROWS,
    column_headers: OptionalSequence = None,
    writer_klass: Type[BaseQuerySetWriter] = BulkQuerySetWriter,
    **writer_kwargs: Any,
) -> HttpResponse:
    """Download queryset as a CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    row_count = write_csv(
        response,
        queryset,
        *columns,
        header=header,
        max_rows=max_rows,
        column_headers=column_headers,
        writer_klass=writer_klass,
        **writer_kwargs,
    )
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

    writer_klass = BulkQuerySetWriter

    def get_writer_klass(self) -> Type[BaseQuerySetWriter]:
        # Override to provide a different writer
        return self.writer_klass

    def get_writer_kwargs(self) -> dict:
        # custom kwargs for initialising the writer
        return {}

    def has_permission(self, request: HttpRequest) -> bool:
        """Return True if the user has permission to download this file."""
        return True

    def get_max_rows(self, request: HttpRequest) -> int:
        """Override to set custom MAX_ROWS on a per-request basis."""
        return MAX_ROWS

    def add_header(self, request: HttpRequest) -> bool:
        """Return True to include header row in CSV."""
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

    def get_columns(self, request: HttpRequest) -> List[str]:
        """Return columns to extract from the queryset."""
        raise NotImplementedError

    def get_column_headers(self, request: HttpRequest) -> List[str]:
        """Return column headers to apply to the CSV."""
        return self.get_columns(request)

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
            header=self.add_header(request),
            max_rows=self.get_max_rows(request),
            column_headers=self.get_column_headers(request),
            writer_klass=self.get_writer_klass(),
            **self.get_writer_kwargs(),
        )
