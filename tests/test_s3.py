from io import BufferedIOBase
from unittest import mock

import pytest
from django.contrib.auth.models import User

from django_csv import csv, s3


@pytest.mark.django_db
@mock.patch("django_csv.s3._upload_fileobj")
def test_upload_multipart(mock_upload):
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    with s3.s3_upload_multipart("bucket_name", "filename") as fileobj:
        row_count = csv.write_csv(fileobj, User.objects.all(), *columns)
        assert row_count == 1
    assert mock_upload.call_count == 1
    call_args = mock_upload.call_args[0]
    assert call_args[0] == "bucket_name"
    assert call_args[1] == "filename"
    assert isinstance(call_args[2], BufferedIOBase)


@pytest.mark.django_db
@mock.patch("django_csv.s3._put_object")
def test_s3_upload(mock_upload):
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    with s3.s3_upload("bucket_name", "filename") as fileobj:
        row_count = csv.write_csv(fileobj, User.objects.all(), *columns)
        assert row_count == 1
    assert mock_upload.call_count == 1
    call_args = mock_upload.call_args[0]
    assert call_args[0] == "bucket_name"
    assert call_args[1] == "filename"
    assert isinstance(call_args[2], BufferedIOBase)


@pytest.mark.parametrize(
    "url,bucket,key",
    [
        ("bucket/key", "bucket", "key"),
        ("bucket/key.csv", "bucket", "key.csv"),
        ("bucket/path/to/key", "bucket", "path/to/key"),
        ("bucket/path/to/key.csv", "bucket", "path/to/key.csv"),
    ],
)
def test_parse_url(url, bucket, key):
    assert s3.parse_url(url) == (bucket, key)


@pytest.mark.parametrize("url", ("", "bucket", "bucket:key", "key.csv"))
def test_parse_url__error(url):
    with pytest.raises(ValueError):
        s3.parse_url(url)
