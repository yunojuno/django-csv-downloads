from django.contrib.auth.models import User
from django.http.request import HttpRequest

from django_csv.csv import QuerySetWriter
from django_csv.views import DownloadCsvView, DownloadForbidden


class DownloadUsers(DownloadCsvView):
    def authorize(self, request: HttpRequest) -> None:
        if not request.user.is_staff:
            raise DownloadForbidden()

    def queryset(self, request: HttpRequest) -> QuerySetWriter:
        return User.objects.all()

    def filename(self, request: HttpRequest) -> str:
        return "users.csv"

    def columns(self, request: HttpRequest) -> str:
        return ("first_name", "last_name")
