from django.contrib.auth.models import User
from django.http.request import HttpRequest

from django_csv.csv import QuerySetWriter
from django_csv.views import CsvDownloadView


class DownloadUsers(CsvDownloadView):

    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_authenticated

    def get_queryset(self, request: HttpRequest) -> QuerySetWriter:
        """Allow staff/superusers to download Users."""
        user = request.user
        if any([user.is_staff, user.is_superuser]):
            return User.objects.all().order_by("first_name", "last_name")
        return User.objects.none()

    def get_filename(self, request: HttpRequest) -> str:
        return "users.csv"

    def get_columns(self, request: HttpRequest) -> str:
        return ("first_name", "last_name")
