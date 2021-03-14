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
from io import BytesIO, TextIOWrapper
from typing import Any

import boto3
from django.db.models import QuerySet

from .settings import MAX_ROWS


class QuerySetWriter:
    """
    Class used to write contents of a QuerySet to a CSV.

    This class wraps the csv.writerow and csv.writerows functions, and
    maps queryset columns to CSV fields (via `values_list`). It is
    initialised with a 'csvfile' where "csvfile can be any object with
    a write() method."

    See https://docs.python.org/3/library/csv.html#csv.writer

    """

    def __init__(
        self,
        csvfile: Any,
        queryset: QuerySet,
        *columns: str,
    ) -> None:
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


def write_csv(csvfile: Any, queryset: QuerySet, *columns: str) -> int:
    """Write QuerySet to fileobj in CSV format."""
    writer = QuerySetWriter(csvfile, queryset, *columns)
    writer.write_header()
    writer.write_rows()
    return writer.row_count


def export_to_s3(bucket: str, key: str, queryset: QuerySet, *columns: str) -> int:
    """
    Export data as a CSV direct to S3.

    This function uses `boto3`, and relies on the environment settings
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, as documented here:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables

    """
    with BytesIO() as csv_bytes:
        # wrap the bytes with a text wrapper so that csv.writer can use it
        with TextIOWrapper(
            csv_bytes,
            encoding="utf-8",
            newline="",
            write_through=True,
        ) as csv_str:
            row_count = write_csv(csv_str, queryset, *columns)
            csv_bytes.seek(0)
            client = boto3.client("s3")
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=csv_bytes,
                ContentType="text/csv",
            )
            return row_count
