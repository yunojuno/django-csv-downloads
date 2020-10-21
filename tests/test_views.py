from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.http.request import HttpRequest

from django_csv.models import CsvDownload
from django_csv.views import download_csv


@pytest.mark.django_db
@mock.patch("django_csv.views.write_csv", lambda *args: 999)
def test_download_csv():
    """Check that download_csv records the download."""
    user = User.objects.create_user("user")
    request = HttpRequest()
    request.user = user
    columns = ("first_name", "last_name")
    response = download_csv(request, "users.csv", User.objects.all(), *columns)
    assert response["Content-Disposition"] == 'attachment; filename="users.csv"'
    assert response["X-Row-Count"] == str(999)
    download = CsvDownload.objects.get()
    assert download.user == user
    assert download.filename == "users.csv"
    assert download.row_count == 999
    assert download.columns == "first_name, last_name"
