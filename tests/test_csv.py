import random
from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse

from django_csv import csv


class TestQuerySetWriter:
    def test_init(self):
        qs = User.objects.none()
        columns = ("first_name", "last_name", "email")
        fileobj = HttpResponse()
        writer = csv.QuerySetWriter(fileobj, qs, *columns)
        assert writer.row_count == 0
        assert writer.columns == columns

    @pytest.mark.django_db
    def test_write_header(self):
        qs = User.objects.none()
        csvfile = StringIO()
        columns = ("first_name", "last_name", "email")
        writer = csv.QuerySetWriter(csvfile, qs, *columns)
        writer.write_header()
        csvfile.seek(0)
        lines = csvfile.readlines()
        assert len(lines) == 1
        assert lines[0].strip() == ",".join(columns)

    @pytest.mark.django_db
    def test_write_rows(self):
        user1 = User.objects.create_user("user1")
        user2 = User.objects.create_user("user2")
        qs = User.objects.all()
        csvfile = StringIO()
        columns = ("first_name", "last_name")
        writer = csv.QuerySetWriter(csvfile, qs, *columns)
        writer.write_rows(max_rows=2)
        csvfile.seek(0)
        lines = csvfile.readlines()
        assert len(lines) == 2

        def assert_row(row, user):
            row = f"{user.first_name},{user.last_name}"

        assert_row(lines[0], user1)
        assert_row(lines[1], user2)


@pytest.mark.django_db
def test_write_csv():
    csvfile = StringIO()
    columns = ("first_name", "last_name")
    User.objects.create_user("user1")
    User.objects.create_user("user2")
    User.objects.create_user("user3")
    row_count = csv.write_csv(csvfile, User.objects.all(), *columns)
    csvfile.seek(0)
    lines = csvfile.readlines()
    assert row_count == 3
    assert len(lines) == 4
