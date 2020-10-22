from django.contrib.auth.models import User
from django.http.request import HttpRequest

from django_csv.csv import QuerySetWriter
from django_csv.views import CsvDownloadView


class DownloadUsers(CsvDownloadView):
    def is_permitted(self, request: HttpRequest) -> bool:
        return request.user.is_staff

    def queryset(self, request: HttpRequest) -> QuerySetWriter:
        return User.objects.all()

    def filename(self, request: HttpRequest) -> str:
        return "users.csv"

    def columns(self, request: HttpRequest) -> str:
        return ("first_name", "last_name")
