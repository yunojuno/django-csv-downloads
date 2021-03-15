"""Optional functions for uploading data direct to S3."""
import contextlib
from io import BytesIO, TextIOWrapper
from typing import Generator

try:
    import boto3
except ImportError:
    raise ImportError("You cannot use the django_csv.s3 module without boto3.")


def _put_object(bucket: str, key: str, body: BytesIO) -> None:
    """Upload binary stream to S3 using put_pubject."""
    client = boto3.client("s3")
    client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="text/csv")


@contextlib.contextmanager
def s3_stream(bucket: str, key: str) -> Generator:
    """
    Return a context manager used to write csv to S3.

    This is a wrapper that provides access to a BytesIO stream (that
    boto3 can use to push a file to S3) via a TextIO wrapper that
    csv.writer can use.

    >>> with s3_stream("bucket", "obj_key") as fileobj:
    ...   write_csv(fileobj, queryset, "col1", "col2")

    """
    with BytesIO() as binary_stream:
        with TextIOWrapper(
            binary_stream, encoding="utf-8", newline="", write_through=True
        ) as text_stream:
            yield text_stream
            binary_stream.seek(0)
            _put_object(bucket, key, binary_stream)
