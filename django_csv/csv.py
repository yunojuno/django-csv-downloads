"""
Functions used to write QuerySet data to a CSV.

This module contains a class (QuerySetWriter) used to wrap up writing of
data from a QuerySet to a CSV (file or HttpResponse).

You should never need to call the QuerySetWriter explicitly - but instead
use the `write_csv` function.

Example of writing to a file:

    >>> qs = MyModel.objects.all()
    >>> cols = ("col1", "col2", "col3")
    >>> with open('foo.csv', 'w') as csvfile:
    >>>     csv.write_csv(csvfile, qs, *cols)
    10

Example of writing to an HttpResponse:

    >>> response = HttpResponse(content_type="text/csv")
    >>> response["Content-Disposition"] = 'attachment; filename="foo.csv"'
    >>> csv.write_csv(response, qs, *cols)
    10

Example of writing to an in-memory text buffer:

    >>> buffer = io.StringIO()
    >>> csv.write_csv(buffer, qs, *cols)
    10

"""
import csv
import logging
from typing import Any

from django.core.paginator import Paginator
from django.db.models import QuerySet

from .settings import DEFAULT_PAGE_SIZE, MAX_ROWS

logger = logging.getLogger(__name__)


class BaseQuerySetWriter:
    """
    Class used to write contents of a QuerySet to a CSV.

    Do not use this class directly - use one of the subclasses, based
    on your expected use case - data size, memory constraints etc.

    This class wraps the csv.writerow and csv.writerows functions, and
    maps queryset columns to CSV fields (via `values_list`). It is
    initialised with a 'csvfile' where "csvfile can be any object with
    a write() method."

    See https://docs.python.org/3/library/csv.html#csv.writer

    """

    def __init__(
        self, csvfile: Any, queryset: QuerySet, *columns: str, max_rows: int = MAX_ROWS
    ) -> None:
        self.writer = csv.writer(csvfile)
        self.queryset = queryset
        self.columns = columns
        self.max_rows = max_rows

    def rows(self) -> QuerySet:
        """Return the rows to write as a capped values_list queryset."""
        return self.queryset.values_list(*self.columns)[: self.max_rows]

    def write_header(self) -> None:
        self.writer.writerow(self.columns)

    def write_rows(self) -> int:
        raise NotImplementedError


class BulkQuerySetWriter(BaseQuerySetWriter):
    """Subclass of QuerySetWriter that writes out queryset in one go."""

    def write_rows(self) -> int:
        """Write the rows out in one go."""
        self.writer.writerows(rows := self.rows())
        return rows.count()


class PagedQuerySetWriter(BaseQuerySetWriter):
    """Subclass of QuerySetWriter that writes out queryset in pages."""

    def __init__(self, *args: Any, page_size: int = DEFAULT_PAGE_SIZE, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.page_size = page_size

    def write_rows(self) -> int:
        """Write the rows out in pages."""
        paginator = Paginator(rows := self.rows(), self.page_size)
        for page_number in paginator.page_range:
            self.writer.writerows(paginator.page(page_number).object_list)
        return rows.count()


class RowQuerySetWriter(BaseQuerySetWriter):
    """Subclass of QuerySetWriter that writes out queryset row-by-row."""

    def write_rows(self, max_rows: int = MAX_ROWS) -> int:
        """Write the rows out one-by-one."""
        for row in (rows := self.rows()).iterator():
            self.writer.writerow(row)
        return rows.count()


def write_csv(
    fileobj: Any,
    queryset: QuerySet,
    *columns: str,
    header: bool = True,
    max_rows: int = MAX_ROWS,
) -> int:
    """Write QuerySet to fileobj in CSV format using BulkQuerySetWriter."""
    writer = BulkQuerySetWriter(fileobj, queryset, *columns, max_rows=max_rows)
    if header:
        writer.write_header()
    return writer.write_rows()
