from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse

from django_csv import csv


class TestBaseQuerySetWriter:
    def test_init(self):
        qs = User.objects.none()
        columns = ("first_name", "last_name", "email")
        fileobj = HttpResponse()
        writer = csv.BaseQuerySetWriter(fileobj, qs, *columns)
        assert writer.columns == columns
        assert writer.queryset == qs
        assert writer.columns == columns
        assert writer.max_rows == csv.MAX_ROWS

    @pytest.mark.django_db
    def test_write_header(self):
        qs = User.objects.none()
        csvfile = StringIO()
        columns = ("first_name", "last_name", "email")
        writer = csv.BaseQuerySetWriter(csvfile, qs, *columns)
        writer.write_header()
        csvfile.seek(0)
        lines = csvfile.readlines()
        assert len(lines) == 1
        assert lines[0].strip() == ",".join(columns)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "klass",
        (csv.BulkQuerySetWriter, csv.PagedQuerySetWriter, csv.RowQuerySetWriter),
    )
    def test_write_rows(self, klass):
        user1 = User.objects.create_user("user1")
        user2 = User.objects.create_user("user2")
        qs = User.objects.all().order_by("id")
        csvfile = StringIO()
        columns = ("first_name", "last_name")
        writer = klass(csvfile, qs, *columns)
        assert writer.write_rows() == 2
        csvfile.seek(0)
        lines = csvfile.readlines()
        assert len(lines) == 2
        assert lines[0].strip() == f"{user1.first_name},{user1.last_name}"
        assert lines[1].strip() == f"{user2.first_name},{user2.last_name}"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "header,max_rows,output_row_count,output_lines",
    [
        (True, 100, 3, 4),
        (False, 100, 3, 3),
        (True, 1, 1, 2),
    ],
)
def test_write_csv(header, max_rows, output_row_count, output_lines):
    csvfile = StringIO()
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    User.objects.create_user("user2")
    User.objects.create_user("user3")
    row_count = csv.write_csv(
        csvfile, User.objects.all(), *columns, header=header, max_rows=max_rows
    )
    csvfile.seek(0)
    lines = csvfile.readlines()
    assert row_count == output_row_count
    assert len(lines) == output_lines
