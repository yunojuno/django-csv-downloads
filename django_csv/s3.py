"""Optional functions for uploading data direct to S3."""
import contextlib
from io import BytesIO, TextIOWrapper
from typing import Generator

try:
    import boto3
except ImportError:
    raise ImportError("You cannot use the django_csv.s3 module without boto3.")


# extracted out to facilitate testing
def _put_object(bucket: str, key: str, fileobj: BytesIO) -> None:
    """Upload binary stream to S3 using put_pubject."""
    client = boto3.client("s3")
    client.put_object(Bucket=bucket, Key=key, Body=fileobj, ContentType="text/csv")


# extracted out to facilitate testing
def _upload_fileobj(bucket: str, key: str, fileobj: BytesIO) -> None:
    """Upload binary stream to S3 using upload_fileobj."""
    client = boto3.client("s3")
    client.upload_fileobj(fileobj, bucket, key)


@contextlib.contextmanager
def s3_stream(bucket: str, key: str, multipart: bool = False) -> Generator:
    """
    Return a context manager used to write csv to S3.

    This is a wrapper that provides access to a BytesIO stream (that boto3 can
    use to push a file to S3) via a TextIO wrapper that csv.writer can use. If

    multipart arg is True this uses the upload_fileobj boto3 function rather
    than put_object (default). This may be a better option for large files.

    >>> with s3_stream("bucket", "obj_key") as fileobj:
    ...   write_csv(fileobj, queryset, "col1", "col2")

    """
    with BytesIO() as fileobj:
        with TextIOWrapper(
            fileobj,
            encoding="utf-8",
            newline="",
            write_through=True,
        ) as buffer:
            yield buffer
            fileobj.seek(0)
            if multipart:
                _upload_fileobj(bucket, key, fileobj)
            else:
                _put_object(bucket, key, fileobj)
