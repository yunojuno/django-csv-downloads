from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from django_csv.views import download_csv

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    actions = ["download"]
    csv_fields = ("first_name", "last_name", "email", "is_staff")

    def download(self, request, queryset):
        """Download selected users as a CSV."""
        return download_csv(request.user, "users.csv", queryset, *self.csv_fields)

    download.short_description = "Download selected users"
