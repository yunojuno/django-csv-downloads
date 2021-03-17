from io import BufferedIOBase
from unittest import mock

import pytest
from django.contrib.auth.models import User

from django_csv import csv, s3


@pytest.mark.django_db
@mock.patch("django_csv.s3._upload_fileobj")
def test_upload_fileobj(mock_upload):
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    with s3.s3_upload_fileobj("bucket_name", "filename") as fileobj:
        row_count = csv.write_csv(fileobj, User.objects.all(), *columns)
        assert row_count == 1
    assert mock_upload.call_count == 1
    call_args = mock_upload.call_args[0]
    assert call_args[0] == "bucket_name"
    assert call_args[1] == "filename"
    assert isinstance(call_args[2], BufferedIOBase)


@pytest.mark.django_db
@mock.patch("django_csv.s3._put_object")
def test_s3_put_object(mock_upload):
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    with s3.s3_put_object("bucket_name", "filename") as fileobj:
        row_count = csv.write_csv(fileobj, User.objects.all(), *columns)
        assert row_count == 1
    assert mock_upload.call_count == 1
    call_args = mock_upload.call_args[0]
    assert call_args[0] == "bucket_name"
    assert call_args[1] == "filename"
    assert isinstance(call_args[2], BufferedIOBase)
