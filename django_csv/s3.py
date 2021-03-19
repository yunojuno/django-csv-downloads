"""Optional functions for uploading data direct to S3."""
import contextlib
from io import BytesIO, TextIOWrapper
from tempfile import TemporaryFile
from typing import IO, Generator, Tuple, Union

from django.db.models import QuerySet

from .csv import write_csv
from .settings import MAX_ROWS

try:
    import boto3
except ImportError:
    raise ImportError("You cannot use the django_csv.s3 module without boto3.")

# type used to smooth over TemporaryFile <> BytesIO mismatch
FileLikeObject = Union[IO[bytes], BytesIO]
# type to represent an S3 address (bucket, key)
S3Url = Tuple[str, str]


# extracted out to facilitate testing
def _put_object(bucket: str, key: str, fileobj: FileLikeObject) -> None:
    """Upload binary stream to S3 using put_pubject."""
    client = boto3.client("s3")
    client.put_object(Bucket=bucket, Key=key, Body=fileobj, ContentType="text/csv")


# extracted out to facilitate testing
def _upload_fileobj(bucket: str, key: str, fileobj: FileLikeObject) -> None:
    """Upload binary stream to S3 using upload_fileobj."""
    client = boto3.client("s3")
    client.upload_fileobj(fileobj, bucket, key)


@contextlib.contextmanager
def s3_upload_multipart(bucket: str, key: str) -> Generator:
    """
    Context manager used to write to S3 using upload_fileobj.

    This context manager writes to a TemporaryFile and then uses the
    multipart boto3 upload function `upload_fileobj`, and is more
    appropriate for large files.

    >>> with s3_upload_fileobj("bucket", "obj_key") as fileobj:
    ...     write_csv(fileobj, queryset, "col1", "col2")

    """
    with TemporaryFile() as fileobj:
        with TextIOWrapper(
            fileobj, encoding="utf-8", newline="", write_through=True
        ) as buffer:
            yield buffer
            fileobj.seek(0)
            _upload_fileobj(bucket, key, fileobj)


@contextlib.contextmanager
def s3_upload(bucket: str, key: str) -> Generator:
    """
    Context manager used to write to S3 using put_object.

    This context manager writes to a in-memory buffer and then uses the
    one-shot boto3 upload function `put_object`, and is more appropriate
    for smaller files.

    >>> with s3_put_object("bucket", "obj_key") as fileobj:
    ...     write_csv(fileobj, queryset, "col1", "col2")

    """
    with BytesIO() as fileobj:
        with TextIOWrapper(
            fileobj, encoding="utf-8", newline="", write_through=True
        ) as buffer:
            yield buffer
            fileobj.seek(0)
            _put_object(bucket, key, fileobj)


def parse_url(url: str) -> S3Url:
    """Parse and validate url."""
    bucket, key = url.split("/", 1)
    if not bucket:
        raise ValueError("Invalid url: bucket is missing.")
    if not key:
        raise ValueError("Invalid url: key is missing.")
    return bucket, key


def write_csv_s3(
    url: str,
    queryset: QuerySet,
    *columns: str,
    header: bool = True,
    max_rows: int = MAX_ROWS,
) -> int:
    """Write a csv to S3."""
    bucket, key = parse_url(url)
    with s3_upload(bucket, key) as fileobj:
        return write_csv(fileobj, queryset, *columns, header=header, max_rows=max_rows)
