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

from django.db.models import QuerySet

from .settings import MAX_ROWS

logger = logging.getLogger(__name__)


class QuerySetWriter:
    """
    Class used to write contents of a QuerySet to a CSV.

    This class wraps the csv.writerow and csv.writerows functions, and
    maps queryset columns to CSV fields (via `values_list`). It is
    initialised with a 'csvfile' where "csvfile can be any object with
    a write() method."

    See https://docs.python.org/3/library/csv.html#csv.writer

    """

    def __init__(self, csvfile: Any, queryset: QuerySet, *columns: str) -> None:
        self._writer = csv.writer(csvfile)
        self.columns = columns
        self.rows = queryset.values_list(*columns)
        self.row_count = 0

    def write_header(self) -> None:
        self._writer.writerow(self.columns)

    def write_rows(self, max_rows: int = MAX_ROWS) -> None:
        """Write QuerySet contents out to CSV and set row_count."""
        self._writer.writerows(rows := self.rows[:max_rows])
        self.row_count = rows.count()


def write_csv(
    csvfile: Any,
    queryset: QuerySet,
    *columns: str,
    header: bool = True,
    max_rows: int = MAX_ROWS,
) -> int:
    """Write QuerySet to fileobj in CSV format."""
    writer = QuerySetWriter(csvfile, queryset, *columns)
    if header:
        writer.write_header()
    writer.write_rows(max_rows=max_rows)
    return writer.row_count
